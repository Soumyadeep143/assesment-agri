# Integration Test Report — Monthly Price Forecasting Notebook

_Generated 2026-11-02 from the real pytest run (`tests/results.json`). Python/pytest executed the notebook's own code cells in a sandbox copy._

Integration tests check **components working together and the deliverable as a whole**: the executed notebook, every sentence of the business-case brief mapped to evidence in the notebook, the end-to-end data flow (cleaning → CV → model → forecast → artifact → API), narrative numbers vs. computed numbers, and the Django / FastAPI / Next.js / React Native snippets (the FastAPI code is **actually executed** with FastAPI's TestClient). Target: **≥ 50 cases**.

## Summary

| Metric | Value |
|---|---|
| Total test cases | **118** |
| Passed | **118** |
| Failed | **0** |
| Skipped | 0 |
| Pass rate | **100.0%** |
| Cumulative test time | 2.8s (excludes the one-off notebook execution fixture) |

## Results by feature area

| Area | Cases | Passed |
|---|---|---|
| 1. Notebook as a deliverable | 25 | 25 |
| 2. Requirement alignment (brief, sentence by sentence) | 26 | 26 |
| 3. Pipeline integration (clean → CV → model → forecast → artifact) | 17 | 17 |
| 4. Narrative numbers vs computed numbers | 13 | 13 |
| 5a. Deployment snippets (Django / Next.js / React Native) | 9 | 9 |
| 5b. FastAPI service executed with TestClient | 19 | 19 |
| 6. Monitoring & business-loop coverage | 9 | 9 |

## Detailed test cases

### 1. Notebook as a deliverable

| ID | Test | What it verifies | Result |
|---|---|---|---|
| I-001 | `test_valid_nbformat` | Notebook validates against nbformat 4 schema | ✅ PASS |
| I-002 | `test_is_ipynb_python3_kernel` | Kernel spec is Python 3 | ✅ PASS |
| I-003 | `test_all_code_cells_executed` | Every code cell has an execution count (outputs are saved in the file) | ✅ PASS |
| I-004 | `test_no_error_outputs_saved` | No cell holds an error output | ✅ PASS |
| I-005 | `test_fresh_run_completes` | A fresh top-to-bottom execution of all cells succeeds (fixture raised nothing) | ✅ PASS |
| I-006 | `test_has_charts` | At least 8 embedded charts | ✅ PASS |
| I-007 | `test_numbered_sections_present[1]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-008 | `test_numbered_sections_present[2]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-009 | `test_numbered_sections_present[3]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-010 | `test_numbered_sections_present[4]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-011 | `test_numbered_sections_present[5]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-012 | `test_numbered_sections_present[6]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-013 | `test_numbered_sections_present[7]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-014 | `test_numbered_sections_present[8]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-015 | `test_numbered_sections_present[9]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-016 | `test_numbered_sections_present[10]` | Sections 1..10 exist (one per business-case question + forecast) | ✅ PASS |
| I-017 | `test_conclusion_present` | Conclusion & limitations section exists | ✅ PASS |
| I-018 | `test_header_has_contact_fields` | Header carries Name / Phone / Email fields (brief: contact details mandatory) | ✅ PASS |
| I-019 | `test_contact_placeholders_flagged_for_user` | MANUAL ITEM: placeholders still present – user must fill name/phone/email before submitting | ✅ PASS |
| I-020 | `test_notebook_size_under_limit` | File small enough for e-mail / WhatsApp (<10 MB) | ✅ PASS |
| I-021 | `test_deliverable_files_exist[price_forecast.ipynb]` | Deliverable files exist in the project folder | ✅ PASS |
| I-022 | `test_deliverable_files_exist[price_data.csv]` | Deliverable files exist in the project folder | ✅ PASS |
| I-023 | `test_deliverable_files_exist[forecast_next_12_months.csv]` | Deliverable files exist in the project folder | ✅ PASS |
| I-024 | `test_deliverable_files_exist[price_model.joblib]` | Deliverable files exist in the project folder | ✅ PASS |
| I-025 | `test_deliverable_files_exist[price_model.json]` | Deliverable files exist in the project folder | ✅ PASS |

### 2. Requirement alignment (brief, sentence by sentence)

| ID | Test | What it verifies | Result |
|---|---|---|---|
| I-026 | `test_requirement_covered[R01 clean: missing values]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-027 | `test_requirement_covered[R02 clean: outliers]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-028 | `test_requirement_covered[R03 clean: anomalies]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-029 | `test_requirement_covered[R04 describe model in detail]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-030 | `test_requirement_covered[R05 explain reasons for selecting model]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-031 | `test_requirement_covered[R06 evaluation metrics]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-032 | `test_requirement_covered[R07 training AND predictive performance]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-033 | `test_requirement_covered[R08 fine-tuning]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-034 | `test_requirement_covered[R09 interpret results]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-035 | `test_requirement_covered[R10 company actions to price changes]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-036 | `test_requirement_covered[R11 how to know actions effective]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-037 | `test_requirement_covered[R12 deploy with Django]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-038 | `test_requirement_covered[R13 Django + FastAPI real-time]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-039 | `test_requirement_covered[R14 integrate APIs into Next.js]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-040 | `test_requirement_covered[R15 integrate APIs into React Native]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-041 | `test_requirement_covered[R16 monitor: performance]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-042 | `test_requirement_covered[R17 monitor: drift]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-043 | `test_requirement_covered[R18 monitor: update model]` | Section text contains the evidence keywords for this requirement | ✅ PASS |
| I-044 | `test_forecast_horizon_12_months` | 'next 12 months': forecast horizon is exactly 12 and starts the month after the last data point | ✅ PASS |
| I-045 | `test_average_monthly_price_target` | Target variable is avg_monthly_price | ✅ PASS |
| I-046 | `test_uses_only_provided_dataset` | 'use only the mentioned dataset': the only data file read is price_data.csv; no web/API data | ✅ PASS |
| I-047 | `test_no_exogenous_data_used` | Model inputs are the price series only (univariate) – consistent with dataset | ✅ PASS |
| I-048 | `test_any_method_allowed_multiple_families` | 'any suitable ML/DL/statistical method': statistical (ETS/ARIMA) and ML (GBM) families compared | ✅ PASS |
| I-049 | `test_trained_on_history_evaluated_on_future` | Rolling-origin CV never trains on the data it is evaluated on (future months only) | ✅ PASS |
| I-050 | `test_dl_decision_documented` | Deep learning consciously considered and excluded with a reason | ✅ PASS |
| I-051 | `test_data_dictionary_fields_respected` | Fields 'date' (ISO YYYY-MM-DD) and 'avg_monthly_price' as per dictionary | ✅ PASS |

### 3. Pipeline integration (clean → CV → model → forecast → artifact)

| ID | Test | What it verifies | Result |
|---|---|---|---|
| I-052 | `test_clean_series_feeds_model` | Final model's level equals the last cleaned log price (alpha=1) | ✅ PASS |
| I-053 | `test_forecast_uses_artifact_level` | Artifact level_log == final fitted level | ✅ PASS |
| I-054 | `test_forecast_to_api_equivalence` | Forecast table == predict() served from the saved artifact | ✅ PASS |
| I-055 | `test_cv_store_reproducible` | Recomputing one CV fold reproduces the stored forecast exactly | ✅ PASS |
| I-056 | `test_cv_to_intervals_flow` | Interval quantiles are computed from the same CV forecasts that were scored | ✅ PASS |
| I-057 | `test_cv_mape_matches_summary_narrative_value` | Headline CV MAPE used in the narrative equals the computed table | ✅ PASS |
| I-058 | `test_fresh_run_matches_saved_forecast` | Determinism: fresh execution reproduces the forecast CSV shipped in the project | ✅ PASS |
| I-059 | `test_fresh_run_matches_saved_artifact` | Determinism: fresh artifact == shipped artifact (same version, alpha, level, quantiles) | ✅ PASS |
| I-060 | `test_saved_outputs_match_fresh_run` | The outputs stored inside the notebook mention the same CV MAPE as the fresh run | ✅ PASS |
| I-061 | `test_cleaning_then_cv_no_nan_propagation` | No NaN anywhere in CV results | ✅ PASS |
| I-062 | `test_cleaning_does_not_leak_future` | Cleaning (neighbour-based) is applied once to history; CV metrics are scored against cleaned data, and robustness check vs RAW actuals stays within 1pp | ✅ PASS |
| I-063 | `test_ensemble_is_mean_of_members` | Ensemble forecast equals the average of SES, ARIMA, GBM | ✅ PASS |
| I-064 | `test_tuned_params_flow_into_models` | Selected ARIMA order from grid is the one used in the tuned model (fits without error on full data) | ✅ PASS |
| I-065 | `test_monitoring_uses_same_model_family` | Monitoring walk-forward 1-step SES errors are consistent with CV 1-step scale (<30% MAPE-rolling median) | ✅ PASS |
| I-066 | `test_drift_flag_consistent_with_volatility_scaling` | Drift detector (PSI>0.25) and stress-band scaler (>1) agree that recent regime is more volatile | ✅ PASS |
| I-067 | `test_stress_band_contains_realised_recent_changes` | Stress 80% band at h=12 would have covered the actual 12-month change from the last 8 origins at least 5/8 times | ✅ PASS |
| I-068 | `test_end_to_end_runtime_reasonable` | Full notebook executes in under 15 minutes | ✅ PASS |

### 4. Narrative numbers vs computed numbers

| ID | Test | What it verifies | Result |
|---|---|---|---|
| I-069 | `test_cv_mape_text` | Narrative '14.8%' equals computed CV MAPE | ✅ PASS |
| I-070 | `test_recent_origin_mape_text` | Narrative 'MAPE 21.4%' for last 8 origins equals computed | ✅ PASS |
| I-071 | `test_holdout_mape_text` | Narrative hold-out 9.1% / train 4.7% equals computed | ✅ PASS |
| I-072 | `test_central_forecast_text` | Narrative central forecast 15,800 -> 15,950 equals computed (rounded to 50) | ✅ PASS |
| I-073 | `test_interval_text` | Narrative 80% band 12,650–22,400 equals computed (rounded to 50) | ✅ PASS |
| I-074 | `test_stress_text` | Narrative stress band 10,700–29,500 equals computed (rounded to 100) | ✅ PASS |
| I-075 | `test_probability_text` | Narrative 41% / 31% / 27–29% equals computed | ✅ PASS |
| I-076 | `test_alpha_text` | Narrative 'α = 1.000' equals computed alpha | ✅ PASS |
| I-077 | `test_origin_count_text` | Narrative '20 origins, 240 forecasts' equals computed | ✅ PASS |
| I-078 | `test_spike_count_text` | Narrative-independent: spike count in saved output = computed (5) | ✅ PASS |
| I-079 | `test_psi_text` | Narrative 'PSI ≈ 1.2' equals computed | ✅ PASS |
| I-080 | `test_vol_text` | Narrative volatility ~1.8x equals computed | ✅ PASS |
| I-081 | `test_replay_text` | Narrative data-quality caveat (Jun-2021 = Oct-2007 = 5,070) is true | ✅ PASS |

### 5a. Deployment snippets (Django / Next.js / React Native)

| ID | Test | What it verifies | Result |
|---|---|---|---|
| I-082 | `test_python_blocks_exist` | At least 4 Python snippets documented (Django service, DRF view, FastAPI service, Django client) | ✅ PASS |
| I-083 | `test_all_python_blocks_parse` | Every Python snippet is syntactically valid | ✅ PASS |
| I-084 | `test_tsx_blocks_exist` | At least 3 TSX snippets (Next.js x2, React Native) | ✅ PASS |
| I-085 | `test_tsx_brackets_balanced` | Brackets/braces/parens balanced in every TSX snippet | ✅ PASS |
| I-086 | `test_nextjs_uses_server_token` | Next.js snippet keeps the token on the server (cookies()) | ✅ PASS |
| I-087 | `test_rn_uses_secure_store` | React Native snippet stores tokens in SecureStore, not AsyncStorage | ✅ PASS |
| I-088 | `test_django_service_logic` | Django services.predict() (stubbed settings) returns the same numbers as the notebook | ✅ PASS |
| I-089 | `test_django_view_validates_horizon` | DRF view constrains horizon to 1..24 | ✅ PASS |
| I-090 | `test_django_client_has_timeout_and_cache` | Django->FastAPI client sets a timeout and caches | ✅ PASS |

### 5b. FastAPI service executed with TestClient

| ID | Test | What it verifies | Result |
|---|---|---|---|
| I-091 | `test_health` | GET /health -> 200 and model version | ✅ PASS |
| I-092 | `test_forecast_requires_key` | No API key -> 422/401 (rejected) | ✅ PASS |
| I-093 | `test_forecast_wrong_key` | Wrong API key -> 401 | ✅ PASS |
| I-094 | `test_forecast_default_12` | Default horizon returns 12 points | ✅ PASS |
| I-095 | `test_forecast_horizon_param[1]` | horizon query parameter respected | ✅ PASS |
| I-096 | `test_forecast_horizon_param[6]` | horizon query parameter respected | ✅ PASS |
| I-097 | `test_forecast_horizon_param[24]` | horizon query parameter respected | ✅ PASS |
| I-098 | `test_forecast_horizon_validation[0]` | Out-of-range horizon -> 422 | ✅ PASS |
| I-099 | `test_forecast_horizon_validation[25]` | Out-of-range horizon -> 422 | ✅ PASS |
| I-100 | `test_forecast_horizon_validation[-3]` | Out-of-range horizon -> 422 | ✅ PASS |
| I-101 | `test_forecast_non_numeric_horizon` | Non-numeric horizon -> 422 | ✅ PASS |
| I-102 | `test_api_matches_notebook` | API numbers equal the notebook's forecast table | ✅ PASS |
| I-103 | `test_api_schema_fields` | Response items carry month/forecast/lo_80/hi_80 | ✅ PASS |
| I-104 | `test_api_band_ordering` | lo_80 < forecast < hi_80 in every API point | ✅ PASS |
| I-105 | `test_openapi_exposed` | OpenAPI schema is published (used to generate typed TS clients) | ✅ PASS |
| I-106 | `test_reload_endpoint_auth` | /admin/reload requires the key | ✅ PASS |
| I-107 | `test_reload_endpoint_works` | /admin/reload reloads the model artifact | ✅ PASS |
| I-108 | `test_hot_swap_new_model_version` | Champion/challenger: replacing the artifact + /admin/reload serves the new version without restart | ✅ PASS |
| I-109 | `test_rollback_restores_version` | Rollback path: reloading the original artifact restores the previous version | ✅ PASS |

### 6. Monitoring & business-loop coverage

| ID | Test | What it verifies | Result |
|---|---|---|---|
| I-110 | `test_alert_rule_fires_on_regime_change` | Rolling-MAPE alert fires at least once on this regime-switching history | ✅ PASS |
| I-111 | `test_monitor_alert_needs_baseline` | Alert threshold = 1.3 x baseline MAPE (rule is explicit in the code) | ✅ PASS |
| I-112 | `test_drift_triggers_retrain_policy_documented` | Section 10 links drift/performance alerts to retraining + rollback | ✅ PASS |
| I-113 | `test_actions_table_covers_three_situations` | Section 5 covers rising, falling and flat/high-uncertainty forecasts | ✅ PASS |
| I-114 | `test_effectiveness_has_counterfactual_and_stats` | Section 6 includes control group, DiD, bootstrap/CI and cost netting | ✅ PASS |
| I-115 | `test_actions_reference_uncertainty_band` | Business actions are tied to the forecast bands (not a point forecast) | ✅ PASS |
| I-116 | `test_deploy_mentions_versioning_and_tests` | Section 7 covers model versioning, CI/CD and a model-regression test | ✅ PASS |
| I-117 | `test_integration_mentions_resilience` | Section 8 covers timeouts, circuit breaker and fallback | ✅ PASS |
| I-118 | `test_frontend_mentions_auth_cors_offline` | Section 9 covers JWT, CORS and offline caching | ✅ PASS |
