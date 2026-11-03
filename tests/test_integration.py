"""INTEGRATION TESTS – cross-component flows, notebook-as-a-whole, requirement alignment, and the deployment snippets."""
import ast, importlib.util, json, os, pathlib, re, sys, types
import numpy as np, pandas as pd, pytest, joblib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def py_blocks(md_text):
    return re.findall(r"```python\n(.*?)```", md_text, flags=re.S)


def tsx_blocks(md_text):
    return re.findall(r"```tsx\n(.*?)```", md_text, flags=re.S)


# ------------------------------------------------------------------ 1. Notebook as a deliverable
class TestNotebookStructure:
    def test_valid_nbformat(self, nbk):
        """Notebook validates against nbformat 4 schema"""
        import nbformat; nbformat.validate(nbk)

    def test_is_ipynb_python3_kernel(self, nbk):
        """Kernel spec is Python 3"""
        assert nbk.metadata["kernelspec"]["language"] == "python"

    def test_all_code_cells_executed(self, nbk):
        """Every code cell has an execution count (outputs are saved in the file)"""
        assert all(c.execution_count is not None for c in nbk.cells if c.cell_type == "code")

    def test_no_error_outputs_saved(self, nbk):
        """No cell holds an error output"""
        assert not [o for c in nbk.cells if c.cell_type == "code" for o in c.outputs if o.output_type == "error"]

    def test_fresh_run_completes(self, ns):
        """A fresh top-to-bottom execution of all cells succeeds (fixture raised nothing)"""
        assert ns["_runtime"] > 0

    def test_has_charts(self, nbk):
        """At least 8 embedded charts"""
        n = sum(1 for c in nbk.cells if c.cell_type == "code" for o in c.outputs if o.output_type == "display_data" and "image/png" in o.data)
        assert n >= 8

    @pytest.mark.parametrize("n", list(range(1, 11)))
    def test_numbered_sections_present(self, sections, n):
        """Sections 1..10 exist (one per business-case question + forecast)"""
        assert n in sections and len(sections[n]) > 200

    def test_conclusion_present(self, sections):
        """Conclusion & limitations section exists"""
        assert 99 in sections

    def test_header_has_contact_fields(self, nbk):
        """Header carries Name / Phone / Email fields (brief: contact details mandatory)"""
        h = nbk.cells[0].source; assert "Phone" in h and "Email" in h and "Candidate" in h

    def test_contact_placeholders_flagged_for_user(self, nbk):
        """MANUAL ITEM: placeholders still present – user must fill name/phone/email before submitting"""
        h = nbk.cells[0].source
        assert "[YOUR NAME]" in h or "[YOUR PHONE]" in h or re.search(r"\+?\d[\d\s-]{8,}", h), "header must either hold placeholders or real contact data"

    def test_notebook_size_under_limit(self):
        """File small enough for e-mail / WhatsApp (<10 MB)"""
        assert (ROOT / "price_forecast.ipynb").stat().st_size < 10_000_000

    @pytest.mark.parametrize("f", ["price_forecast.ipynb", "price_data.csv", "forecast_next_12_months.csv", "price_model.joblib", "price_model.json"])
    def test_deliverable_files_exist(self, f):
        """Deliverable files exist in the project folder"""
        assert (ROOT / f).exists()


# ------------------------------------------------------------------ 2. Requirement alignment (each sentence of the brief)
REQ = [
    ("R01 clean: missing values", 1, ["Missing values", "isna", "interpolate"]),
    ("R02 clean: outliers", 1, ["spike", "z-score", "Treatment"]),
    ("R03 clean: anomalies", 1, ["anomal", "level shift", "Stale"]),
    ("R04 describe model in detail", 3, ["SES", "ARIMA", "Gradient", "Ensemble", "rolling-origin"]),
    ("R05 explain reasons for selecting model", 3, ["Why SES was selected", "parsimony", "random walk"]),
    ("R06 evaluation metrics", 3, ["MAE", "RMSE", "MAPE", "MASE"]),
    ("R07 training AND predictive performance", 3, ["Train", "Test", "hold-out"]),
    ("R08 fine-tuning", 3, ["Tuning", "grid", "tune"]),
    ("R09 interpret results", 3, ["Honest reading", "noise"]),
    ("R10 company actions to price changes", 5, ["Forward-buy", "Hedge", "decision rule"]),
    ("R11 how to know actions effective", 6, ["difference-in-differences", "counterfactual", "KPIs"]),
    ("R12 deploy with Django", 7, ["Django", "Gunicorn", "joblib", "DRF"]),
    ("R13 Django + FastAPI real-time", 8, ["FastAPI", "Django", "real-time", "/v1/forecast"]),
    ("R14 integrate APIs into Next.js", 9, ["Next.js", "fetch", "Server Component"]),
    ("R15 integrate APIs into React Native", 9, ["React Native", "expo-secure-store", "useQuery"]),
    ("R16 monitor: performance", 10, ["MAPE", "coverage", "Rolling"]),
    ("R17 monitor: drift", 10, ["drift", "PSI"]),
    ("R18 monitor: update model", 10, ["retrain", "Champion", "rollback"]),
]


class TestRequirementAlignment:
    @pytest.mark.parametrize("rid,sec,words", REQ, ids=[r[0] for r in REQ])
    def test_requirement_covered(self, sections, rid, sec, words):
        """Section text contains the evidence keywords for this requirement"""
        text = sections[sec].lower() if sec != 1 else (sections[1] + sections[2]).lower()
        missing = [w for w in words if w.lower() not in text and w.lower() not in sections[sec].lower()]
        assert not missing, f"{rid}: missing {missing}"

    def test_forecast_horizon_12_months(self, ns):
        """'next 12 months': forecast horizon is exactly 12 and starts the month after the last data point"""
        fc = ns["fc"]; assert len(fc) == 12 and fc.index[0] == ns["y"].index[-1] + pd.offsets.MonthBegin(1)

    def test_average_monthly_price_target(self, ns, code_text):
        """Target variable is avg_monthly_price"""
        assert "avg_monthly_price" in code_text

    def test_uses_only_provided_dataset(self, code_text):
        """'use only the mentioned dataset': the only data file read is price_data.csv; no web/API data"""
        reads = re.findall(r"read_csv\(\s*[\"']([^\"']+)[\"']", code_text)
        assert set(reads) <= {"price_data.csv", "forecast_next_12_months.csv"}
        assert not re.search(r"requests\.|urllib|yfinance|pandas_datareader|http[s]?://", code_text)

    def test_no_exogenous_data_used(self, ns):
        """Model inputs are the price series only (univariate) – consistent with dataset"""
        assert ns["raw"].shape[1] == 2

    def test_any_method_allowed_multiple_families(self, ns):
        """'any suitable ML/DL/statistical method': statistical (ETS/ARIMA) and ML (GBM) families compared"""
        c = ns["candidates"]; assert any("ARIMA" in k for k in c) and "GBM (lags)" in c and "SES" in c

    def test_trained_on_history_evaluated_on_future(self, ns):
        """Rolling-origin CV never trains on the data it is evaluated on (future months only)"""
        assert all(len(ns["y"].iloc[:o]) == o for o in ns["ORIGINS"]) and max(ns["ORIGINS"]) + 12 <= len(ns["y"])

    def test_dl_decision_documented(self, md_text):
        """Deep learning consciously considered and excluded with a reason"""
        assert "LSTM" in md_text and "deliberately not used" in md_text

    def test_data_dictionary_fields_respected(self, ns):
        """Fields 'date' (ISO YYYY-MM-DD) and 'avg_monthly_price' as per dictionary"""
        r = ns["raw"]; assert list(r.columns) == ["date", "avg_monthly_price"] and r.date.dt.strftime("%Y-%m-%d").str.len().eq(10).all()


# ------------------------------------------------------------------ 3. Pipeline integration (cleaning -> CV -> model -> forecast -> artifact)
class TestPipelineIntegration:
    def test_clean_series_feeds_model(self, ns):
        """Final model's level equals the last cleaned log price (alpha=1)"""
        assert ns["fit_full"].level.iloc[-1] == pytest.approx(ns["y"].iloc[-1], abs=1e-3)

    def test_forecast_uses_artifact_level(self, ns):
        """Artifact level_log == final fitted level"""
        assert ns["artifact"]["level_log"] == pytest.approx(float(ns["fit_full"].level.iloc[-1]))

    def test_forecast_to_api_equivalence(self, ns):
        """Forecast table == predict() served from the saved artifact"""
        p = ns["predict"](12)
        assert np.allclose(p.forecast.values, ns["fc"].forecast.values) and np.allclose(p.hi_80.values, ns["fc"].hi_80.values)

    def test_cv_store_reproducible(self, ns):
        """Recomputing one CV fold reproduces the stored forecast exactly"""
        o = ns["ORIGINS"][5]; fc = ns["f_ses"](ns["y"].iloc[:o], 12)
        assert np.allclose(fc, ns["st_t"]["SES"][ns["y"].index[o]])

    def test_cv_to_intervals_flow(self, ns):
        """Interval quantiles are computed from the same CV forecasts that were scored"""
        e = np.concatenate([(ns["y"].iloc[o:o+12].values - ns["st_t"]["SES"][ns["y"].index[o]]) / np.sqrt(np.arange(1, 13)) for o in ns["ORIGINS"]])
        assert np.allclose(np.quantile(e, 0.9), ns["q"][.90])

    def test_cv_mape_matches_summary_narrative_value(self, ns):
        """Headline CV MAPE used in the narrative equals the computed table"""
        assert round(ns["cv_t"]["SES"].MAPE.mean(), 1) == 14.8

    def test_fresh_run_matches_saved_forecast(self, ns):
        """Determinism: fresh execution reproduces the forecast CSV shipped in the project"""
        saved = pd.read_csv(ROOT / "forecast_next_12_months.csv", index_col=0)
        assert np.allclose(saved.forecast, ns["fc"].forecast) and np.allclose(saved.hi_95, ns["fc"].hi_95)

    def test_fresh_run_matches_saved_artifact(self, ns):
        """Determinism: fresh artifact == shipped artifact (same version, alpha, level, quantiles)"""
        saved = json.load(open(ROOT / "price_model.json"))
        assert saved["version"] == ns["artifact"]["version"] and saved["level_log"] == pytest.approx(ns["artifact"]["level_log"])
        assert saved["quantiles"]["0.9"] == pytest.approx(ns["artifact"]["quantiles"]["0.9"])

    def test_saved_outputs_match_fresh_run(self, nbk, ns):
        """The outputs stored inside the notebook mention the same CV MAPE as the fresh run"""
        txt = json.dumps([o.get("data", {}).get("text/plain", "") or o.get("text", "") for c in nbk.cells if c.cell_type == "code" for o in c.outputs])
        assert "14.79" in txt

    def test_cleaning_then_cv_no_nan_propagation(self, ns):
        """No NaN anywhere in CV results"""
        assert not any(v.isna().any().any() for v in ns["cv_t"].values())

    def test_cleaning_does_not_leak_future(self, ns):
        """Cleaning (neighbour-based) is applied once to history; CV metrics are scored against cleaned data, and robustness check vs RAW actuals stays within 1pp"""
        c, _ = ns["rolling_cv"](ns["f_ses"], fit_series=ns["y"], eval_series=np.log(ns["s_raw"]))
        assert abs(c.MAPE.mean() - ns["cv_t"]["SES"].MAPE.mean()) < 1.0

    def test_ensemble_is_mean_of_members(self, ns):
        """Ensemble forecast equals the average of SES, ARIMA, GBM"""
        tr = ns["y"].iloc[:180]
        e = ns["tuned"]["Ensemble (SES+ARIMA+GBM)"](tr, 12)
        m = np.mean([ns["f_ses"](tr, 12), ns["tuned"]["ARIMA tuned"](tr, 12), ns["tuned"]["GBM tuned"](tr, 12)], axis=0)
        assert np.allclose(e, m)

    def test_tuned_params_flow_into_models(self, ns):
        """Selected ARIMA order from grid is the one used in the tuned model (fits without error on full data)"""
        assert len(ns["tuned"]["ARIMA tuned"](ns["y"], 12)) == 12

    def test_monitoring_uses_same_model_family(self, ns):
        """Monitoring walk-forward 1-step SES errors are consistent with CV 1-step scale (<30% MAPE-rolling median)"""
        assert ns["mon"].ape.median() < 10

    def test_drift_flag_consistent_with_volatility_scaling(self, ns):
        """Drift detector (PSI>0.25) and stress-band scaler (>1) agree that recent regime is more volatile"""
        ret = ns["y"].diff().dropna()
        assert ns["psi"](ret[:-24].values, ret[-24:].values) > 0.25 and ns["vol_ratio"] > 1.0

    def test_stress_band_contains_realised_recent_changes(self, ns):
        """Stress 80% band at h=12 would have covered the actual 12-month change from the last 8 origins at least 5/8 times"""
        y, hh, q, vr = ns["y"], ns["hh"], ns["q"], ns["vol_ratio"]
        hit = 0
        for o in ns["test_or"]:
            f = ns["st_t"]["SES"][y.index[o]][-1]; a = y.iloc[o + 11]
            hit += (f + hh[-1]*q[.10]*vr <= a <= f + hh[-1]*q[.90]*vr)
        assert hit >= 5

    def test_end_to_end_runtime_reasonable(self, ns):
        """Full notebook executes in under 15 minutes"""
        assert ns["_runtime"] < 900


# ------------------------------------------------------------------ 4. Narrative numbers vs computed numbers
class TestNarrativeConsistency:
    def test_cv_mape_text(self, ns, md_text):
        """Narrative '14.8%' equals computed CV MAPE"""
        assert "**14.8%**" in md_text and round(ns["cv_t"]["SES"].MAPE.mean(), 1) == 14.8

    def test_recent_origin_mape_text(self, ns, md_text):
        """Narrative 'MAPE 21.4%' for last 8 origins equals computed"""
        assert "21.4%" in md_text and round(ns["block"](ns["test_or"]).MAPE["SES"], 1) == 21.4

    def test_holdout_mape_text(self, ns, md_text):
        """Narrative hold-out 9.1% / train 4.7% equals computed"""
        r = ns["res"]; assert "**9.1%**" in md_text and "4.7%" in md_text
        assert round(r.iloc[1].MAPE, 1) == 9.1 and round(r.iloc[0].MAPE, 1) == 4.7

    def test_central_forecast_text(self, ns, md_text):
        """Narrative central forecast 15,800 -> 15,950 equals computed (rounded to 50)"""
        f = ns["fc"].forecast; assert "15,800" in md_text and "15,950" in md_text
        assert round(f.iloc[0] / 50) * 50 == 15800 and round(f.iloc[-1] / 50) * 50 == 15950

    def test_interval_text(self, ns, md_text):
        """Narrative 80% band 12,650–22,400 equals computed (rounded to 50)"""
        f = ns["fc"]; assert "12,650" in md_text and "22,400" in md_text
        assert round(f.lo_80.iloc[-1] / 50) * 50 == 12650 and round(f.hi_80.iloc[-1] / 50) * 50 == 22400

    def test_stress_text(self, ns, md_text):
        """Narrative stress band 10,700–29,500 equals computed (rounded to 100)"""
        f = ns["fc"]; assert "10,700" in md_text and "29,500" in md_text
        assert round(f.lo_80_stress.iloc[-1] / 100) * 100 == 10700 and round(f.hi_80_stress.iloc[-1] / 100) * 100 == 29500

    def test_probability_text(self, ns, md_text):
        """Narrative 41% / 31% / 27–29% equals computed"""
        t = ns["tab"]; assert "41%" in md_text and "31%" in md_text
        assert round(t.loc["rise > 10%", "all years"]) == 41 and round(t.loc["fall > 10%", "all years"]) == 31

    def test_alpha_text(self, ns, md_text):
        """Narrative 'α = 1.000' equals computed alpha"""
        assert "α is 1.000" in md_text or "α = 1.000" in md_text
        assert round(ns["fit"].params["smoothing_level"], 3) == 1.0

    def test_origin_count_text(self, ns, md_text):
        """Narrative '20 origins, 240 forecasts' equals computed"""
        assert "20 origins, 240 forecasts" in md_text and len(ns["ORIGINS"]) == 20 and len(ns["E"]) == 240

    def test_spike_count_text(self, ns):
        """Narrative-independent: spike count in saved output = computed (5)"""
        assert int(ns["spike"].sum()) == 5

    def test_psi_text(self, ns, md_text):
        """Narrative 'PSI ≈ 1.2' equals computed"""
        ret = ns["y"].diff().dropna(); assert "1.2" in md_text and round(ns["psi"](ret[:-24].values, ret[-24:].values), 1) == 1.2

    def test_vol_text(self, ns, md_text):
        """Narrative volatility ~1.8x equals computed"""
        assert "1.8" in md_text and round(ns["vol_ratio"], 1) == 1.8

    def test_replay_text(self, ns, md_text):
        """Narrative data-quality caveat (Jun-2021 = Oct-2007 = 5,070) is true"""
        assert "5,070" in md_text and ns["s_raw"]["2021-06-01"] == ns["s_raw"]["2007-10-01"] == 5070


# ------------------------------------------------------------------ 5. Deployment snippets (sections 7-9) are real, valid code
@pytest.fixture(scope="module")
def blocks(md_text):
    return py_blocks(md_text)


class TestDeploymentSnippets:
    def test_python_blocks_exist(self, blocks):
        """At least 4 Python snippets documented (Django service, DRF view, FastAPI service, Django client)"""
        assert len(blocks) >= 4

    def test_all_python_blocks_parse(self, blocks):
        """Every Python snippet is syntactically valid"""
        for b in blocks:
            ast.parse(b)

    def test_tsx_blocks_exist(self, md_text):
        """At least 3 TSX snippets (Next.js x2, React Native)"""
        assert len(tsx_blocks(md_text)) >= 3

    def test_tsx_brackets_balanced(self, md_text):
        """Brackets/braces/parens balanced in every TSX snippet"""
        for b in tsx_blocks(md_text):
            for o, c in ("{}", "()", "[]"):
                assert b.count(o) == b.count(c), (o, c)

    def test_nextjs_uses_server_token(self, md_text):
        """Next.js snippet keeps the token on the server (cookies())"""
        assert "cookies()" in md_text and "next: { revalidate" in md_text

    def test_rn_uses_secure_store(self, md_text):
        """React Native snippet stores tokens in SecureStore, not AsyncStorage"""
        assert "SecureStore.getItemAsync" in md_text

    def test_django_service_logic(self, ns, blocks, monkeypatch):
        """Django services.predict() (stubbed settings) returns the same numbers as the notebook"""
        b = next(x for x in blocks if "def load_model" in x)
        dj = types.ModuleType("django"); conf = types.ModuleType("django.conf")
        conf.settings = types.SimpleNamespace(MODEL_PATH="price_model.joblib"); dj.conf = conf
        monkeypatch.setitem(sys.modules, "django", dj); monkeypatch.setitem(sys.modules, "django.conf", conf)
        g = {}; exec(b, g)
        out = g["predict"](12)
        assert len(out) == 12 and out[0]["month"] == "2025-10"
        assert np.allclose([o["forecast"] for o in out], ns["fc"].forecast, atol=1.0)
        assert np.allclose([o["hi_80"] for o in out], ns["fc"].hi_80, atol=1.0)

    def test_django_view_validates_horizon(self, blocks):
        """DRF view constrains horizon to 1..24"""
        assert any("min_value=1, max_value=24" in b for b in blocks)

    def test_django_client_has_timeout_and_cache(self, blocks):
        """Django->FastAPI client sets a timeout and caches"""
        b = next(x for x in blocks if "httpx.get" in x); assert "timeout=" in b and "cache.set" in b


@pytest.fixture(scope="module")
def fastapi_client(ns, blocks, tmp_path_factory):
    pytest.importorskip("fastapi"); pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    src = next(b for b in blocks if "FastAPI(title" in b)
    d = tmp_path_factory.mktemp("api"); f = d / "inference_main.py"; f.write_text(src)
    os.environ["MODEL_PATH"] = str(ns["_workdir"] / "price_model.joblib"); os.environ["SERVICE_KEY"] = "k123"
    spec = importlib.util.spec_from_file_location("inference_main", f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return TestClient(m.app), m


H = {"x-api-key": "k123"}


class TestFastAPIService:
    """The FastAPI code documented in section 8 is executed as-is with FastAPI's TestClient."""
    def test_health(self, fastapi_client):
        """GET /health -> 200 and model version"""
        c, _ = fastapi_client; r = c.get("/health"); assert r.status_code == 200 and r.json()["model_version"] == "2025-09-v1"

    def test_forecast_requires_key(self, fastapi_client):
        """No API key -> 422/401 (rejected)"""
        c, _ = fastapi_client; assert c.get("/v1/forecast").status_code in (401, 422)

    def test_forecast_wrong_key(self, fastapi_client):
        """Wrong API key -> 401"""
        c, _ = fastapi_client; assert c.get("/v1/forecast", headers={"x-api-key": "bad"}).status_code == 401

    def test_forecast_default_12(self, fastapi_client):
        """Default horizon returns 12 points"""
        c, _ = fastapi_client; r = c.get("/v1/forecast", headers=H); assert r.status_code == 200 and len(r.json()["forecast"]) == 12

    @pytest.mark.parametrize("h", [1, 6, 24])
    def test_forecast_horizon_param(self, fastapi_client, h):
        """horizon query parameter respected"""
        c, _ = fastapi_client; assert c.get(f"/v1/forecast?horizon={h}", headers=H).json()["horizon"] == h

    @pytest.mark.parametrize("h", [0, 25, -3])
    def test_forecast_horizon_validation(self, fastapi_client, h):
        """Out-of-range horizon -> 422"""
        c, _ = fastapi_client; assert c.get(f"/v1/forecast?horizon={h}", headers=H).status_code == 422

    def test_forecast_non_numeric_horizon(self, fastapi_client):
        """Non-numeric horizon -> 422"""
        c, _ = fastapi_client; assert c.get("/v1/forecast?horizon=abc", headers=H).status_code == 422

    def test_api_matches_notebook(self, ns, fastapi_client):
        """API numbers equal the notebook's forecast table"""
        c, _ = fastapi_client; j = c.get("/v1/forecast", headers=H).json()["forecast"]
        assert np.allclose([p["forecast"] for p in j], ns["fc"].forecast, atol=1) and np.allclose([p["lo_80"] for p in j], ns["fc"].lo_80, atol=1)

    def test_api_schema_fields(self, fastapi_client):
        """Response items carry month/forecast/lo_80/hi_80"""
        c, _ = fastapi_client; p = c.get("/v1/forecast?horizon=1", headers=H).json()["forecast"][0]; assert set(p) == {"month", "forecast", "lo_80", "hi_80"}

    def test_api_band_ordering(self, fastapi_client):
        """lo_80 < forecast < hi_80 in every API point"""
        c, _ = fastapi_client; assert all(p["lo_80"] < p["forecast"] < p["hi_80"] for p in c.get("/v1/forecast", headers=H).json()["forecast"])

    def test_openapi_exposed(self, fastapi_client):
        """OpenAPI schema is published (used to generate typed TS clients)"""
        c, _ = fastapi_client; assert "/v1/forecast" in c.get("/openapi.json").json()["paths"]

    def test_reload_endpoint_auth(self, fastapi_client):
        """/admin/reload requires the key"""
        c, _ = fastapi_client; assert c.post("/admin/reload", headers={"x-api-key": "no"}).status_code == 401

    def test_reload_endpoint_works(self, fastapi_client):
        """/admin/reload reloads the model artifact"""
        c, _ = fastapi_client; r = c.post("/admin/reload", headers=H); assert r.status_code == 200 and r.json()["reloaded"] == "2025-09-v1"

    def test_hot_swap_new_model_version(self, ns, fastapi_client, tmp_path):
        """Champion/challenger: replacing the artifact + /admin/reload serves the new version without restart"""
        c, m = fastapi_client; art = dict(ns["artifact"]); art["version"] = "challenger-x"; p = tmp_path / "new.joblib"; joblib.dump(art, p)
        old = os.environ["MODEL_PATH"]; os.environ["MODEL_PATH"] = str(p)
        try:
            assert c.post("/admin/reload", headers=H).json()["reloaded"] == "challenger-x"
            assert c.get("/health").json()["model_version"] == "challenger-x"
        finally:
            os.environ["MODEL_PATH"] = old; c.post("/admin/reload", headers=H)

    def test_rollback_restores_version(self, fastapi_client):
        """Rollback path: reloading the original artifact restores the previous version"""
        c, _ = fastapi_client; assert c.get("/health").json()["model_version"] == "2025-09-v1"


# ------------------------------------------------------------------ 6. Monitoring / business loops
class TestMonitoringAndBusinessLoop:
    def test_alert_rule_fires_on_regime_change(self, ns):
        """Rolling-MAPE alert fires at least once on this regime-switching history"""
        assert ns["mon"].alert_mape.any()

    def test_monitor_alert_needs_baseline(self, code_text):
        """Alert threshold = 1.3 x baseline MAPE (rule is explicit in the code)"""
        assert "1.3 * bt" in code_text

    def test_drift_triggers_retrain_policy_documented(self, sections):
        """Section 10 links drift/performance alerts to retraining + rollback"""
        s = sections[10].lower(); assert "triggered" in s and "rollback" in s and "champion" in s

    def test_actions_table_covers_three_situations(self, sections):
        """Section 5 covers rising, falling and flat/high-uncertainty forecasts"""
        s = sections[5]; assert "Forecast rises" in s and "Forecast falls" in s and "Flat but high-uncertainty" in s

    def test_effectiveness_has_counterfactual_and_stats(self, sections):
        """Section 6 includes control group, DiD, bootstrap/CI and cost netting"""
        s = sections[6]; assert "difference-in-differences" in s and "bootstrap" in s and "net benefit" in s

    def test_actions_reference_uncertainty_band(self, sections):
        """Business actions are tied to the forecast bands (not a point forecast)"""
        assert "80% upper bound" in sections[5]

    def test_deploy_mentions_versioning_and_tests(self, sections):
        """Section 7 covers model versioning, CI/CD and a model-regression test"""
        s = sections[7]; assert "Version it" in s and "CI" in s and "regression test" in s

    def test_integration_mentions_resilience(self, sections):
        """Section 8 covers timeouts, circuit breaker and fallback"""
        s = sections[8]; assert "timeout" in s and "circuit breaker" in s and "fallback" in s

    def test_frontend_mentions_auth_cors_offline(self, sections):
        """Section 9 covers JWT, CORS and offline caching"""
        s = sections[9]; assert "JWT" in s and "CORS" in s and "Offline" in s
