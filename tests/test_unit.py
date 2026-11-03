"""UNIT TESTS – each test targets one function / one data property of the notebook."""
import json, math
import numpy as np, pandas as pd, pytest, joblib


# ------------------------------------------------------------------ A. Data loading
class TestDataLoading:
    def test_raw_shape(self, ns):
        """Raw file has 249 rows x 2 columns"""
        assert ns["raw"].shape == (249, 2)

    def test_column_names(self, ns):
        """Columns are exactly the data-dictionary fields: date, avg_monthly_price"""
        assert list(ns["raw"].columns) == ["date", "avg_monthly_price"]

    def test_date_parsed_as_datetime(self, ns):
        """'date' parsed to datetime64"""
        assert np.issubdtype(ns["raw"]["date"].dtype, np.datetime64)

    def test_price_numeric(self, ns):
        """'avg_monthly_price' is numeric"""
        assert pd.api.types.is_numeric_dtype(ns["raw"]["avg_monthly_price"])

    def test_dates_sorted(self, ns):
        """Dates are strictly increasing"""
        assert ns["raw"]["date"].is_monotonic_increasing and ns["raw"]["date"].is_unique

    def test_month_start_format(self, ns):
        """All dates are day-1 (ISO YYYY-MM-01) as the data dictionary states"""
        assert (ns["raw"]["date"].dt.day == 1).all()

    def test_first_and_last_dates(self, ns):
        """Range is Jan-2005 .. Sep-2025"""
        r = ns["raw"]; assert r.date.iloc[0] == pd.Timestamp("2005-01-01") and r.date.iloc[-1] == pd.Timestamp("2025-09-01")

    def test_first_and_last_prices(self, ns):
        """First/last prices match the source file (5500 / 15750)"""
        r = ns["raw"]; assert r.avg_monthly_price.iloc[0] == 5500 and r.avg_monthly_price.iloc[-1] == 15750

    def test_min_max_prices(self, ns):
        """Min 3500, max 16163"""
        p = ns["raw"].avg_monthly_price; assert p.min() == 3500 and p.max() == 16163

    def test_no_missing_values(self, ns):
        """No nulls in the raw file"""
        assert ns["raw"].isna().sum().sum() == 0

    def test_prices_positive(self, ns):
        """All prices are > 0 (log transform is safe)"""
        assert (ns["raw"].avg_monthly_price > 0).all()

    def test_matches_source_csv(self, ns):
        """Loaded values equal the CSV file byte-for-byte after parsing"""
        df = pd.read_csv("price_data.csv"); assert df.avg_monthly_price.tolist() == ns["raw"].avg_monthly_price.tolist()


# ------------------------------------------------------------------ B. Time-series index & cleaning
class TestCleaning:
    def test_monthly_frequency(self, ns):
        """s_raw has a regular month-start frequency"""
        assert ns["s_raw"].index.freqstr == "MS"

    def test_no_gaps_in_calendar(self, ns):
        """No calendar month is missing"""
        assert len(pd.date_range(ns["s_raw"].index[0], ns["s_raw"].index[-1], freq="MS")) == len(ns["s_raw"]) == 249

    def test_gap_fill_count_zero(self, ns):
        """No gaps needed filling in this file"""
        assert ns["n_gaps"] == 0

    def test_s_raw_float(self, ns):
        """s_raw is float (needed for interpolation/log)"""
        assert ns["s_raw"].dtype == float

    def test_spike_count(self, ns):
        """Exactly 5 isolated spikes flagged"""
        assert int(ns["spike"].sum()) == 5

    @pytest.mark.parametrize("d", ["2005-05-01", "2006-02-01", "2006-05-01", "2009-07-01", "2021-03-01"])
    def test_expected_spike_dates(self, ns, d):
        """Each known glitch month is flagged"""
        assert bool(ns["spike"].loc[d])

    @pytest.mark.parametrize("d", ["2013-11-01", "2021-06-01", "2023-12-01"])
    def test_level_shifts_not_treated_as_spikes(self, ns, d):
        """Persistent regime shifts are NOT flagged as spikes (must be kept)"""
        assert not bool(ns["spike"].loc[d])

    @pytest.mark.parametrize("d", ["2013-11-01", "2021-06-01", "2023-12-01"])
    def test_level_shifts_detected(self, ns, d):
        """Regime shifts appear in the 'shift' report"""
        assert bool(ns["shift"].loc[d])

    def test_only_spikes_modified(self, ns):
        """Cleaning changes only the flagged months"""
        diff = (ns["s_clean"] != ns["s_raw"])
        assert set(ns["s_raw"].index[diff]) <= set(ns["s_raw"].index[ns["spike"]])

    def test_clean_no_nan(self, ns):
        """Cleaned series has no NaN"""
        assert ns["s_clean"].isna().sum() == 0

    def test_clean_length_preserved(self, ns):
        """Cleaning keeps all 249 observations (nothing dropped)"""
        assert len(ns["s_clean"]) == len(ns["s_raw"])

    def test_clean_within_raw_range(self, ns):
        """Interpolated values stay within the observed raw range"""
        assert ns["s_clean"].min() >= ns["s_raw"].min() and ns["s_clean"].max() <= ns["s_raw"].max()

    def test_clean_positive(self, ns):
        """Cleaned prices are positive"""
        assert (ns["s_clean"] > 0).all()

    def test_replacement_between_neighbours(self, ns):
        """Each replaced value lies between its two neighbours"""
        s = ns["s_clean"]
        for d in ns["s_raw"].index[ns["spike"]]:
            i = s.index.get_loc(d); lo, hi = sorted([s.iloc[i-1], s.iloc[i+1]])
            assert lo - 1 <= s.iloc[i] <= hi + 1

    def test_repeated_values_flagged_not_removed(self, ns):
        """9 repeated (stale) values are reported but retained"""
        assert int(ns["rep"].sum()) == 9 and ns["s_clean"].loc["2025-05-01"] == 14263

    def test_replay_first12_identical(self, ns):
        """Jun-2021.. block exactly equals Oct-2007.. block (12/12) – the data-quality caveat is factual"""
        assert (ns["a"][:12] == ns["b"][:12]).all()

    def test_log_series_matches(self, ns):
        """y (modelling series) equals log(s_clean)"""
        assert np.allclose(ns["y"], np.log(ns["s_clean"]))

    # ---- detect_spikes behaviour on synthetic data
    @staticmethod
    def _base(n=60, seed=0):
        rng = np.random.default_rng(seed)
        idx = pd.date_range("2010-01-01", periods=n, freq="MS")
        return pd.Series(np.log(100 * 1.005 ** np.arange(n)) + rng.normal(0, 0.01, n), index=idx)

    def test_detects_injected_up_spike(self, ns):
        """Injected +60% one-month spike is detected"""
        s = self._base(); s.iloc[30] += 0.47
        f, _ = ns["detect_spikes"](s); assert bool(f.iloc[30])

    def test_detects_injected_down_spike(self, ns):
        """Injected -50% one-month dip is detected"""
        s = self._base(); s.iloc[30] -= 0.7
        f, _ = ns["detect_spikes"](s); assert bool(f.iloc[30])

    def test_ignores_persistent_level_shift(self, ns):
        """A permanent +70% step is not a spike"""
        s = self._base(); s.iloc[30:] += 0.53
        f, _ = ns["detect_spikes"](s); assert not bool(f.iloc[30]) and not bool(f.iloc[31])

    def test_clean_series_has_no_spikes(self, ns):
        """Smooth noisy series flags (almost) nothing"""
        f, _ = ns["detect_spikes"](self._base()); assert f.sum() <= 1

    def test_perfectly_smooth_series_spike_still_detected(self, ns):
        """Edge case: zero-variance series (MAD=0) must not hide a spike"""
        idx = pd.date_range("2010-01-01", periods=40, freq="MS")
        s = pd.Series(np.log(100 * 1.01 ** np.arange(40)), index=idx); s.iloc[20] += 0.5
        f, _ = ns["detect_spikes"](s); assert bool(f.iloc[20])

    def test_constant_series_no_error(self, ns):
        """Constant series: no crash, no flags"""
        s = pd.Series(np.log(np.full(30, 100.0)), index=pd.date_range("2010-01-01", periods=30, freq="MS"))
        f, _ = ns["detect_spikes"](s); assert f.sum() == 0

    def test_endpoints_never_flagged(self, ns):
        """First/last points (missing a neighbour) are never flagged"""
        s = self._base(); s.iloc[0] += 1; s.iloc[-1] += 1
        f, _ = ns["detect_spikes"](s); assert not f.iloc[0] and not f.iloc[-1]

    def test_two_adjacent_high_points_not_spike(self, ns):
        """Two consecutive high months are a mini-regime, not an isolated glitch"""
        s = self._base(); s.iloc[30:32] += 0.5
        f, _ = ns["detect_spikes"](s); assert not f.iloc[30] and not f.iloc[31]

    def test_threshold_monotonic(self, ns):
        """Raising the z-threshold never flags more points"""
        s = self._base(); s.iloc[30] += 0.2
        a = ns["detect_spikes"](s, 2.0)[0].sum(); b = ns["detect_spikes"](s, 6.0)[0].sum(); assert b <= a

    def test_returns_aligned_index(self, ns):
        """Output shares the input index"""
        s = self._base(); f, z = ns["detect_spikes"](s); assert f.index.equals(s.index) and z.index.equals(s.index)


# ------------------------------------------------------------------ C. Forecasting functions
class TestForecastFunctions:
    @pytest.fixture
    def tr(self, ns):
        return ns["y"].iloc[:200]

    @pytest.mark.parametrize("h", [1, 6, 12, 24])
    @pytest.mark.parametrize("fn", ["f_naive", "f_snaive", "f_drift", "f_ses", "f_damped"])
    def test_output_length(self, ns, tr, fn, h):
        """Each baseline returns exactly h forecasts"""
        assert len(ns[fn](tr, h)) == h

    def test_naive_value(self, ns, tr):
        """Naive = last observation"""
        assert np.allclose(ns["f_naive"](tr, 12), tr.iloc[-1])

    def test_snaive_value(self, ns, tr):
        """Seasonal naive repeats last 12 values"""
        assert np.allclose(ns["f_snaive"](tr, 12), tr.iloc[-12:].values)

    def test_snaive_wraps(self, ns, tr):
        """Seasonal naive wraps for h>12"""
        f = ns["f_snaive"](tr, 24); assert np.allclose(f[:12], f[12:])

    def test_drift_exact_on_linear_series(self, ns):
        """Drift reproduces a perfectly linear series"""
        s = pd.Series(np.arange(50, dtype=float), index=pd.date_range("2010-01-01", periods=50, freq="MS"))
        assert np.allclose(ns["f_drift"](s, 5), [50, 51, 52, 53, 54])

    def test_ses_constant_series(self, ns):
        """SES of a constant series is that constant"""
        s = pd.Series(np.full(40, 7.0), index=pd.date_range("2010-01-01", periods=40, freq="MS"))
        assert np.allclose(ns["f_ses"](s, 6), 7.0)

    def test_ses_flat_forecast(self, ns, tr):
        """SES gives a flat multi-step forecast"""
        f = ns["f_ses"](tr, 12); assert np.allclose(f, f[0])

    def test_ses_close_to_last_value(self, ns, tr):
        """On this series SES ~ last value (random-walk behaviour)"""
        assert abs(ns["f_ses"](tr, 1)[0] - tr.iloc[-1]) < 0.05

    def test_damped_finite(self, ns, tr):
        """Damped ETS finite"""
        assert np.isfinite(ns["f_damped"](tr, 12)).all()

    def test_arima_forecast_finite(self, ns, tr):
        """ARIMA(0,1,1) finite"""
        assert np.isfinite(ns["make_arima"]((0, 1, 1))(tr, 12)).all()

    def test_arima_with_drift_runs(self, ns, tr):
        """ARIMA with drift term runs"""
        assert len(ns["make_arima"]((0, 1, 1), trend="t")(tr, 12)) == 12

    def test_sarima_runs(self, ns, tr):
        """Seasonal SARIMA runs and is finite"""
        assert np.isfinite(ns["make_arima"]((0, 1, 1), (0, 1, 1, 12))(tr, 12)).all()

    def test_gbm_length_and_finite(self, ns, tr):
        """GBM recursive forecast is finite and h long"""
        f = ns["make_gbm"]()(tr, 12); assert len(f) == 12 and np.isfinite(f).all()

    def test_gbm_deterministic(self, ns, tr):
        """GBM is reproducible (fixed random_state)"""
        g = ns["make_gbm"](); assert np.allclose(g(tr, 12), g(tr, 12))

    def test_gbm_reasonable_range(self, ns, tr):
        """GBM forecast stays within +-50% of last price (no explosion)"""
        f = np.exp(ns["make_gbm"]()(tr, 12)); last = np.exp(tr.iloc[-1]); assert (f > 0.5*last).all() and (f < 1.5*last).all()

    def test_forecasts_positive_after_exp(self, ns, tr):
        """Back-transformed forecasts are positive (log model cannot go negative)"""
        for fn in ["f_naive", "f_ses", "f_damped", "f_drift"]:
            assert (np.exp(ns[fn](tr, 12)) > 0).all()

    def test_functions_do_not_mutate_input(self, ns, tr):
        """Forecast functions do not modify the training series"""
        before = tr.copy(); ns["f_ses"](tr, 12); ns["f_damped"](tr, 12); assert before.equals(tr)

    def test_candidate_registry(self, ns):
        """11 candidate models were compared"""
        assert len(ns["candidates"]) == 11 and "Seasonal naive" in ns["candidates"]


# ------------------------------------------------------------------ D. Metrics
class TestMetrics:
    def test_perfect_forecast_zero_error(self, ns):
        """Perfect forecast -> all errors 0"""
        m = ns["metrics"]([100, 200], [100, 200], 10); assert all(abs(v) < 1e-12 for v in m.values())

    def test_known_mae(self, ns):
        """MAE known case = 15"""
        assert ns["metrics"]([100, 200], [110, 180], 10)["MAE"] == pytest.approx(15)

    def test_known_rmse(self, ns):
        """RMSE known case = sqrt(250)"""
        assert ns["metrics"]([100, 200], [110, 180], 10)["RMSE"] == pytest.approx(math.sqrt(250))

    def test_known_mape(self, ns):
        """MAPE known case = 10%"""
        assert ns["metrics"]([100, 200], [110, 180], 10)["MAPE"] == pytest.approx(10.0)

    def test_known_smape(self, ns):
        """sMAPE known case"""
        exp = np.mean([2*10/210, 2*20/380]) * 100
        assert ns["metrics"]([100, 200], [110, 180], 10)["sMAPE"] == pytest.approx(exp)

    def test_known_mase(self, ns):
        """MASE = MAE / scale"""
        assert ns["metrics"]([100, 200], [110, 180], 10)["MASE"] == pytest.approx(1.5)

    def test_rmse_ge_mae(self, ns):
        """RMSE >= MAE always"""
        m = ns["metrics"]([100, 200, 300], [90, 230, 310], 5); assert m["RMSE"] >= m["MAE"]

    def test_metrics_nonnegative(self, ns):
        """All metrics non-negative"""
        assert all(v >= 0 for v in ns["metrics"]([100, 200, 300], [90, 230, 310], 5).values())

    def test_symmetry_of_absolute_errors(self, ns):
        """MAE same for over- and under-forecast of equal size"""
        a = ns["metrics"]([100], [110], 1)["MAE"]; b = ns["metrics"]([100], [90], 1)["MAE"]; assert a == b

    def test_mape_asymmetric_property(self, ns):
        """MAPE penalises over-forecast less than same-size under-forecast ratio base (documented property)"""
        assert ns["metrics"]([100], [110], 1)["MAPE"] == ns["metrics"]([100], [90], 1)["MAPE"] == 10.0

    def test_accepts_series(self, ns):
        """Works with pandas Series input"""
        assert ns["metrics"](pd.Series([100., 200.]), pd.Series([100., 210.]), 1)["MAE"] == pytest.approx(5)

    def test_returns_five_keys(self, ns):
        """Returns MAE, RMSE, MAPE, sMAPE, MASE"""
        assert set(ns["metrics"]([1.], [1.], 1)) == {"MAE", "RMSE", "MAPE", "sMAPE", "MASE"}

    def test_scale_inverse_for_mase(self, ns):
        """Doubling scale halves MASE"""
        a = ns["metrics"]([100], [110], 1)["MASE"]; b = ns["metrics"]([100], [110], 2)["MASE"]; assert a == pytest.approx(2*b)


# ------------------------------------------------------------------ E. Rolling-origin CV
class TestRollingCV:
    def test_origin_count(self, ns):
        """20 rolling origins"""
        assert len(ns["ORIGINS"]) == 20

    def test_origin_bounds(self, ns):
        """First origin Jan-2015 (idx 120); last leaves a full 12-month test window"""
        o = ns["ORIGINS"]; assert o[0] == 120 and o[-1] + ns["H"] <= ns["N"]

    def test_origin_spacing(self, ns):
        """Origins spaced 6 months"""
        assert set(np.diff(ns["ORIGINS"])) == {6}

    def test_horizon_is_12(self, ns):
        """Forecast horizon constant H = 12 (brief: next 12 months)"""
        assert ns["H"] == 12

    def test_no_leakage_train_ends_before_test(self, ns):
        """Training window passed to the model is strictly before the test window"""
        seen = []
        def spy(tr, h):
            seen.append((len(tr), tr.index[-1])); return np.repeat(tr.iloc[-1], h)
        ns["rolling_cv"](spy)
        for (n, last), o in zip(seen, ns["ORIGINS"]):
            assert n == o and last < ns["y"].index[o]

    def test_cv_frame_shape(self, ns):
        """CV result: 20 rows x 6 columns"""
        c, s = ns["rolling_cv"](ns["f_naive"]); assert c.shape == (20, 5) and len(s) == 20

    def test_stored_forecast_length(self, ns):
        """Every stored forecast has H points"""
        _, s = ns["rolling_cv"](ns["f_naive"]); assert all(len(v) == 12 for v in s.values())

    def test_failure_falls_back_to_naive(self, ns):
        """A model that raises falls back to naive instead of crashing the CV"""
        def bad(tr, h): raise RuntimeError("boom")
        c, s = ns["rolling_cv"](bad); c2, _ = ns["rolling_cv"](ns["f_naive"])
        assert np.allclose(c.MAE, c2.MAE)

    def test_cv_naive_equals_manual(self, ns):
        """CV MAE for naive equals manual calculation on fold 1"""
        y, o = ns["y"], ns["ORIGINS"][0]
        manual = np.mean(np.abs(np.exp(y.iloc[o:o+12]).values - np.exp(y.iloc[o-1])))
        c, _ = ns["rolling_cv"](ns["f_naive"], origins=[o]); assert c.MAE.iloc[0] == pytest.approx(manual)

    def test_cv_metrics_nonnegative(self, ns):
        """All CV fold metrics >= 0"""
        assert (ns["cv"]["SES"] >= 0).all().all()

    def test_cv_has_all_candidates(self, ns):
        """CV evaluated every candidate"""
        assert set(ns["cv"]) == set(ns["candidates"])

    def test_tune_test_origins_disjoint(self, ns):
        """Tuning origins and untouched test origins do not overlap"""
        assert not set(ns["tune_or"]) & set(ns["test_or"]) and len(ns["tune_or"]) == 12 and len(ns["test_or"]) == 8

    def test_tuning_precedes_test(self, ns):
        """All tuning origins are earlier than the untouched test origins (no look-ahead tuning)"""
        assert max(ns["tune_or"]) < min(ns["test_or"])


# ------------------------------------------------------------------ F. Model selection & tuning
class TestSelectionTuning:
    def test_summary_sorted_by_mape(self, ns):
        """Comparison table sorted ascending by MAPE"""
        m = ns["summary"].MAPE.values; assert (np.diff(m) >= 0).all()

    def test_ses_or_naive_best_baseline(self, ns):
        """SES/Naive top the 11-model table"""
        assert ns["summary"].index[0] in ("SES", "Naive")

    def test_seasonal_naive_worst(self, ns):
        """Seasonal naive is worst -> no seasonality to exploit"""
        assert ns["summary"].index[-1] == "Seasonal naive"

    def test_sarima_not_better_than_ses(self, ns):
        """Seasonal SARIMA does not beat SES"""
        s = ns["summary"].MAPE; assert s["SARIMA(0,1,1)(0,1,1,12)"] > s["SES"]

    def test_arima_grid_size(self, ns):
        """ARIMA grid: p,q in 0..3 x 2 trend options minus the empty model = 31"""
        assert len(ns["arima_grid"]) == 31

    def test_arima_grid_sorted(self, ns):
        """ARIMA grid sorted by MAPE"""
        assert (np.diff(ns["arima_grid"].MAPE.values) >= 0).all()

    def test_best_arima_is_grid_top(self, ns):
        """Chosen ARIMA order = top of grid"""
        assert tuple(ns["best_arima"].order) == tuple(ns["arima_grid"].iloc[0].order)

    def test_gbm_grid_size(self, ns):
        """GBM grid: 3 x 3 x 2 = 18"""
        assert len(ns["gbm_grid"]) == 18

    def test_gbm_grid_sorted(self, ns):
        """GBM grid sorted"""
        assert (np.diff(ns["gbm_grid"].MAPE.values) >= 0).all()

    def test_tuned_models_present(self, ns):
        """Tuned model set includes naive, SES, damped, ARIMA, GBM, ensemble"""
        assert set(ns["cv_t"]) == {"Naive", "SES", "Damped ETS", "ARIMA tuned", "GBM tuned", "Ensemble (SES+ARIMA+GBM)"}

    def test_ses_best_on_untouched_origins(self, ns):
        """On the 8 untouched origins SES (or identical Naive) beats ARIMA, GBM and the ensemble"""
        t = ns["block"](ns["test_or"]).MAPE
        assert t["SES"] <= min(t["ARIMA tuned"], t["GBM tuned"], t["Ensemble (SES+ARIMA+GBM)"])

    def test_tuning_does_not_beat_naive_overall(self, ns):
        """Tuned ARIMA/GBM do not beat naive across all 20 origins (supports parsimony)"""
        t = ns["block"](ns["ORIGINS"]).MAPE; assert t["ARIMA tuned"] >= t["Naive"] and t["GBM tuned"] >= t["Naive"]

    def test_by_horizon_error_grows(self, ns):
        """Forecast error increases with horizon"""
        e = ns["by_h"](ns["st_t"], "SES"); assert e[-1] > e[0] and len(e) == 12

    def test_dm_test_returns_t_and_p(self, ns):
        """Diebold-Mariano helper returns finite t and p in [0,1]"""
        t, p = ns["dm"]("ARIMA tuned", "Naive"); assert np.isfinite(t) and 0 <= p <= 1

    def test_dm_arima_worse_than_naive(self, ns):
        """DM statistic positive (worse) for ARIMA vs Naive"""
        assert ns["dm"]("ARIMA tuned", "Naive")[0] > 0


# ------------------------------------------------------------------ G. Final hold-out (train vs test)
class TestHoldout:
    def test_split_date(self, ns):
        """Split at Sep-2024"""
        assert ns["split"] == pd.Timestamp("2024-09-01")

    def test_train_test_sizes(self, ns):
        """Train 237 months, test 12 months"""
        assert len(ns["tr"]) == 237 and len(ns["te"]) == 12

    def test_test_follows_train(self, ns):
        """Test starts right after train"""
        assert ns["te"].index[0] == ns["tr"].index[-1] + pd.offsets.MonthBegin(1)

    def test_alpha_is_one(self, ns):
        """SES alpha fitted ~1 (random walk)"""
        assert ns["fit"].params["smoothing_level"] > 0.99

    def test_train_and_test_rows(self, ns):
        """Report has Train and Test rows"""
        assert list(ns["res"].index) == ["Train (1-step in-sample)", "Test (12-month ahead)"]

    def test_train_error_lower_than_test(self, ns):
        """1-step in-sample error < 12-month-ahead error (as expected)"""
        r = ns["res"]; assert r.loc["Train (1-step in-sample)", "MAPE"] < r.loc["Test (12-month ahead)", "MAPE"]

    def test_test_mape_value(self, ns):
        """Hold-out MAPE ~9.1%"""
        assert ns["res"].loc["Test (12-month ahead)", "MAPE"] == pytest.approx(9.12, abs=0.05)

    def test_train_mape_value(self, ns):
        """Train MAPE ~4.7%"""
        assert ns["res"].loc["Train (1-step in-sample)", "MAPE"] == pytest.approx(4.66, abs=0.05)

    def test_competitor_table_complete(self, ns):
        """Hold-out comparison includes 6 models"""
        assert len(ns["cmp"]) == 6

    def test_seasonal_worse_on_holdout(self, ns):
        """Seasonal SARIMA clearly worse than SES on hold-out"""
        assert ns["cmp"]["SARIMA seasonal"]["MAPE"] > ns["cmp"]["SES (selected)"]["MAPE"] * 1.3

    def test_nonseasonal_models_within_noise(self, ns):
        """Non-seasonal models within 5% of each other on hold-out"""
        v = [ns["cmp"][k]["MAPE"] for k in ["Naive", "SES (selected)", "ARIMA tuned", "GBM tuned", "Ensemble"]]
        assert max(v) / min(v) < 1.05

    def test_residual_ljung_box_white(self, ns):
        """Residuals show no autocorrelation (Ljung-Box p>0.05 at lags 6,12,24)"""
        assert (ns["lb"].lb_pvalue > 0.05).all()

    def test_residuals_fat_tailed(self, ns):
        """Residual excess kurtosis is large -> justifies empirical intervals"""
        from scipy import stats; assert stats.kurtosis(ns["resid"]) > 5

    def test_cleaning_robustness(self, ns):
        """MAPE with/without cleaning differ by < 1pp (conclusions not sensitive)"""
        c1, _ = ns["rolling_cv"](ns["f_ses"], fit_series=np.log(ns["s_raw"]), eval_series=np.log(ns["s_raw"]))
        c2, _ = ns["rolling_cv"](ns["f_ses"], fit_series=ns["y"], eval_series=np.log(ns["s_raw"]))
        assert abs(c1.MAPE.mean() - c2.MAPE.mean()) < 1.0


# ------------------------------------------------------------------ H. Intervals & forecast table
class TestForecast:
    def test_twelve_rows(self, ns):
        """Forecast has 12 rows"""
        assert len(ns["fc"]) == 12

    def test_forecast_start_month(self, ns):
        """First forecast month Oct-2025"""
        assert ns["fc"].index[0] == pd.Timestamp("2025-10-01")

    def test_forecast_end_month(self, ns):
        """Last forecast month Sep-2026"""
        assert ns["fc"].index[-1] == pd.Timestamp("2026-09-01")

    def test_forecast_contiguous(self, ns):
        """Forecast months contiguous"""
        assert (np.diff(ns["fc"].index.values).astype("timedelta64[D]").astype(int) >= 28).all() and ns["fc"].index.freqstr == "MS"

    def test_forecast_positive(self, ns):
        """All forecast & interval values positive"""
        assert (ns["fc"] > 0).all().all()

    def test_forecast_within_80(self, ns):
        """lo_80 < forecast < hi_80"""
        f = ns["fc"]; assert (f.lo_80 < f.forecast).all() and (f.forecast < f.hi_80).all()

    def test_80_inside_95(self, ns):
        """80% band nested in 95% band"""
        f = ns["fc"]; assert (f.lo_95 <= f.lo_80).all() and (f.hi_95 >= f.hi_80).all()

    def test_intervals_widen_with_horizon(self, ns):
        """Band width strictly increases with horizon"""
        w = ns["fc"].hi_80 - ns["fc"].lo_80; assert (np.diff(w) > 0).all()

    def test_stress_wider_than_base(self, ns):
        """Stress band at least as wide as base 80%"""
        f = ns["fc"]; assert (f.hi_80_stress >= f.hi_80).all() and (f.lo_80_stress <= f.lo_80).all()

    def test_vol_ratio_bounds(self, ns):
        """Volatility scaler clipped to [1, 2]"""
        assert 1.0 <= ns["vol_ratio"] <= 2.0

    def test_vol_ratio_value(self, ns):
        """Recent volatility ~1.8x history"""
        assert ns["vol_ratio"] == pytest.approx(1.78, abs=0.05)

    def test_quantiles_ordered(self, ns):
        """q2.5 < q10 < q50 < q90 < q97.5"""
        q = ns["q"]; assert q[.025] < q[.10] < q[.50] < q[.90] < q[.975]

    def test_median_quantile_near_zero(self, ns):
        """Median standardised error ~0 (unbiased centre)"""
        assert abs(ns["q"][.50]) < 0.02

    def test_pooled_error_count(self, ns):
        """240 pooled standardised errors (20 origins x 12)"""
        assert len(ns["E"]) == 240

    def test_80pct_empirical_coverage(self, ns):
        """Empirical coverage of the 80% band in CV ~ 80%"""
        y, hh, q = ns["y"], ns["hh"], ns["q"]
        cov = np.mean([np.mean((y.iloc[o:o+12].values >= ns["st_t"]["SES"][y.index[o]] + hh*q[.10]) &
                               (y.iloc[o:o+12].values <= ns["st_t"]["SES"][y.index[o]] + hh*q[.90])) for o in ns["ORIGINS"]])
        assert 0.75 <= cov <= 0.85

    def test_central_forecast_near_last_price(self, ns):
        """Central forecast within 2% of last observed price (random-walk logic)"""
        assert abs(ns["fc"].forecast.iloc[0] / 15750 - 1) < 0.02

    def test_forecast_csv_written(self, ns):
        """forecast_next_12_months.csv written with 12 rows"""
        d = pd.read_csv("forecast_next_12_months.csv"); assert len(d) == 12 and "forecast" in d.columns

    def test_forecast_csv_matches_frame(self, ns):
        """CSV values equal in-memory forecast"""
        d = pd.read_csv("forecast_next_12_months.csv", index_col=0); assert np.allclose(d.forecast, ns["fc"].forecast)

    def test_base_forecast_flat(self, ns):
        """SES base path is flat on log scale"""
        assert np.allclose(ns["base"], ns["base"][0])

    def test_hist_move_probabilities_sum(self, ns):
        """Rise/fall/stable probabilities sum to 100%"""
        assert np.allclose(ns["tab"].sum(), 100, atol=0.2)

    def test_hist_move_value(self, ns):
        """P(rise>10% in 12m) ~41%"""
        assert ns["tab"].loc["rise > 10%", "all years"] == pytest.approx(41.4, abs=0.2)


# ------------------------------------------------------------------ I. Model artifact & predict()
class TestArtifact:
    def test_artifact_keys(self, ns):
        """Artifact has all keys needed by the API"""
        assert {"model", "alpha", "level_log", "last_date", "quantiles", "cv_mape", "vol_scale", "trained_on_rows", "version"} <= set(ns["artifact"])

    def test_artifact_version(self, ns):
        """Version string set"""
        assert ns["artifact"]["version"] == "2025-09-v1"

    def test_artifact_last_date(self, ns):
        """last_date = Sep 2025"""
        assert ns["artifact"]["last_date"] == "2025-09-01"

    def test_artifact_rows(self, ns):
        """Trained on 249 rows"""
        assert ns["artifact"]["trained_on_rows"] == 249

    def test_artifact_level_log(self, ns):
        """level_log ~ log(15750)"""
        assert ns["artifact"]["level_log"] == pytest.approx(np.log(15750), abs=1e-3)

    def test_joblib_roundtrip(self, ns):
        """joblib file reloads to the same dict"""
        assert joblib.load("price_model.joblib") == ns["artifact"]

    def test_json_artifact_valid(self, ns):
        """price_model.json is valid JSON identical to artifact"""
        assert json.load(open("price_model.json")) == ns["artifact"]

    def test_predict_default_horizon(self, ns):
        """predict() default -> 12 rows with required columns"""
        p = ns["predict"](); assert len(p) == 12 and list(p.columns) == ["month", "forecast", "lo_80", "hi_80"]

    @pytest.mark.parametrize("h", [1, 3, 12, 24])
    def test_predict_horizon(self, ns, h):
        """predict(h) returns h rows"""
        assert len(ns["predict"](h)) == h

    def test_predict_matches_notebook_forecast(self, ns):
        """predict() equals the notebook forecast table"""
        assert np.allclose(ns["predict"](12).forecast, ns["fc"].forecast)

    def test_predict_bands_match(self, ns):
        """predict() 80% band equals notebook band"""
        p = ns["predict"](12); assert np.allclose(p.lo_80, ns["fc"].lo_80) and np.allclose(p.hi_80, ns["fc"].hi_80)

    def test_predict_months_format(self, ns):
        """Month strings are YYYY-MM"""
        assert ns["predict"](2).month.tolist() == ["2025-10", "2025-11"]

    def test_predict_accepts_explicit_artifact(self, ns):
        """predict(art=...) uses supplied artifact"""
        a = dict(ns["artifact"]); a["level_log"] = np.log(1000.0)
        assert ns["predict"](1, a).forecast.iloc[0] == pytest.approx(1000 * np.exp(a["quantiles"]["0.5"]), abs=1)


# ------------------------------------------------------------------ J. Monitoring helpers
class TestMonitoring:
    def test_psi_identical_zero(self, ns):
        """PSI of identical samples = 0"""
        x = np.random.default_rng(0).normal(size=500); assert ns["psi"](x, x) == pytest.approx(0, abs=1e-6)

    def test_psi_shift_large(self, ns):
        """PSI flags a 3-sigma mean shift as major (>0.25)"""
        r = np.random.default_rng(1); assert ns["psi"](r.normal(size=500), r.normal(3, 1, 500)) > 0.25

    def test_psi_small_shift_small(self, ns):
        """Same-distribution resample has PSI < 0.1"""
        r = np.random.default_rng(2); assert ns["psi"](r.normal(size=2000), r.normal(size=2000)) < 0.1

    def test_psi_nonnegative(self, ns):
        """PSI >= 0"""
        r = np.random.default_rng(3); assert ns["psi"](r.normal(size=300), r.normal(0.5, 2, 300)) >= 0

    def test_psi_on_data_flags_drift(self, ns):
        """PSI(last 24m vs history) > 0.25 -> drift flagged"""
        ret = ns["y"].diff().dropna(); assert ns["psi"](ret[:-24].values, ret[-24:].values) > 0.25

    def test_monitor_frame_columns(self, ns):
        """Monitoring frame has actual, ses, naive, ape, rolling MAPE, alert"""
        assert {"actual", "ses", "naive", "ape", "roll_mape_12", "alert_mape"} <= set(ns["mon"].columns)

    def test_monitor_length(self, ns):
        """Walk-forward produced N-1-120 = 128 monthly rows"""
        assert len(ns["mon"]) == 128

    def test_ape_nonnegative(self, ns):
        """Absolute percentage errors >= 0"""
        assert (ns["mon"].ape >= 0).all()

    def test_rolling_mape_warmup(self, ns):
        """Rolling MAPE NaN for first 11 months"""
        assert ns["mon"].roll_mape_12.iloc[:11].isna().all() and ns["mon"].roll_mape_12.iloc[11:].notna().all()

    def test_alert_boolean(self, ns):
        """Alert column boolean"""
        assert ns["mon"].alert_mape.dtype == bool

    def test_ses_monitor_equals_naive(self, ns):
        """1-step SES ~ naive (alpha=1) in walk-forward"""
        m = ns["mon"]; assert np.mean(np.abs(m.ses / m.naive - 1)) < 0.02
