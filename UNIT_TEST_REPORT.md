# Unit Test Report — Monthly Price Forecasting Notebook

_Generated 2026-11-02 from the real pytest run (`tests/results.json`). Python/pytest executed the notebook's own code cells in a sandbox copy._

Unit tests check **one function or one data property at a time**: schema of the CSV, each cleaning rule (including synthetic spike/level-shift inputs), each forecasting function, each metric against hand-computed values, the rolling-CV mechanics (including a no-leakage spy test), tuning grids, hold-out figures, interval maths, the saved artifact and `predict()`, and monitoring helpers. Target: **≥ 100 cases**.

## Summary

| Metric | Value |
|---|---|
| Total test cases | **187** |
| Passed | **187** |
| Failed | **0** |
| Skipped | 0 |
| Pass rate | **100.0%** |
| Cumulative test time | 2.8s (excludes the one-off notebook execution fixture) |

## Results by feature area

| Area | Cases | Passed |
|---|---|---|
| A. Data loading & schema (data dictionary) | 12 | 12 |
| B. Cleaning: missing values, outliers, anomalies | 35 | 35 |
| C. Forecasting functions (baselines, ETS, ARIMA, GBM) | 37 | 37 |
| D. Evaluation metrics | 13 | 13 |
| E. Rolling-origin cross-validation | 13 | 13 |
| F. Model selection & fine-tuning | 15 | 15 |
| G. Train vs test hold-out, residuals, robustness | 14 | 14 |
| H. 12-month forecast & intervals | 21 | 21 |
| I. Model artifact & predict() | 16 | 16 |
| J. Monitoring helpers (PSI, rolling MAPE) | 11 | 11 |

## Detailed test cases

### A. Data loading & schema (data dictionary)

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-001 | `test_raw_shape` | Raw file has 249 rows x 2 columns | ✅ PASS |
| U-002 | `test_column_names` | Columns are exactly the data-dictionary fields: date, avg_monthly_price | ✅ PASS |
| U-003 | `test_date_parsed_as_datetime` | 'date' parsed to datetime64 | ✅ PASS |
| U-004 | `test_price_numeric` | 'avg_monthly_price' is numeric | ✅ PASS |
| U-005 | `test_dates_sorted` | Dates are strictly increasing | ✅ PASS |
| U-006 | `test_month_start_format` | All dates are day-1 (ISO YYYY-MM-01) as the data dictionary states | ✅ PASS |
| U-007 | `test_first_and_last_dates` | Range is Jan-2005 .. Sep-2025 | ✅ PASS |
| U-008 | `test_first_and_last_prices` | First/last prices match the source file (5500 / 15750) | ✅ PASS |
| U-009 | `test_min_max_prices` | Min 3500, max 16163 | ✅ PASS |
| U-010 | `test_no_missing_values` | No nulls in the raw file | ✅ PASS |
| U-011 | `test_prices_positive` | All prices are > 0 (log transform is safe) | ✅ PASS |
| U-012 | `test_matches_source_csv` | Loaded values equal the CSV file byte-for-byte after parsing | ✅ PASS |

### B. Cleaning: missing values, outliers, anomalies

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-013 | `test_monthly_frequency` | s_raw has a regular month-start frequency | ✅ PASS |
| U-014 | `test_no_gaps_in_calendar` | No calendar month is missing | ✅ PASS |
| U-015 | `test_gap_fill_count_zero` | No gaps needed filling in this file | ✅ PASS |
| U-016 | `test_s_raw_float` | s_raw is float (needed for interpolation/log) | ✅ PASS |
| U-017 | `test_spike_count` | Exactly 5 isolated spikes flagged | ✅ PASS |
| U-018 | `test_expected_spike_dates[2005-05-01]` | Each known glitch month is flagged | ✅ PASS |
| U-019 | `test_expected_spike_dates[2006-02-01]` | Each known glitch month is flagged | ✅ PASS |
| U-020 | `test_expected_spike_dates[2006-05-01]` | Each known glitch month is flagged | ✅ PASS |
| U-021 | `test_expected_spike_dates[2009-07-01]` | Each known glitch month is flagged | ✅ PASS |
| U-022 | `test_expected_spike_dates[2021-03-01]` | Each known glitch month is flagged | ✅ PASS |
| U-023 | `test_level_shifts_not_treated_as_spikes[2013-11-01]` | Persistent regime shifts are NOT flagged as spikes (must be kept) | ✅ PASS |
| U-024 | `test_level_shifts_not_treated_as_spikes[2021-06-01]` | Persistent regime shifts are NOT flagged as spikes (must be kept) | ✅ PASS |
| U-025 | `test_level_shifts_not_treated_as_spikes[2023-12-01]` | Persistent regime shifts are NOT flagged as spikes (must be kept) | ✅ PASS |
| U-026 | `test_level_shifts_detected[2013-11-01]` | Regime shifts appear in the 'shift' report | ✅ PASS |
| U-027 | `test_level_shifts_detected[2021-06-01]` | Regime shifts appear in the 'shift' report | ✅ PASS |
| U-028 | `test_level_shifts_detected[2023-12-01]` | Regime shifts appear in the 'shift' report | ✅ PASS |
| U-029 | `test_only_spikes_modified` | Cleaning changes only the flagged months | ✅ PASS |
| U-030 | `test_clean_no_nan` | Cleaned series has no NaN | ✅ PASS |
| U-031 | `test_clean_length_preserved` | Cleaning keeps all 249 observations (nothing dropped) | ✅ PASS |
| U-032 | `test_clean_within_raw_range` | Interpolated values stay within the observed raw range | ✅ PASS |
| U-033 | `test_clean_positive` | Cleaned prices are positive | ✅ PASS |
| U-034 | `test_replacement_between_neighbours` | Each replaced value lies between its two neighbours | ✅ PASS |
| U-035 | `test_repeated_values_flagged_not_removed` | 9 repeated (stale) values are reported but retained | ✅ PASS |
| U-036 | `test_replay_first12_identical` | Jun-2021.. block exactly equals Oct-2007.. block (12/12) – the data-quality caveat is factual | ✅ PASS |
| U-037 | `test_log_series_matches` | y (modelling series) equals log(s_clean) | ✅ PASS |
| U-038 | `test_detects_injected_up_spike` | Injected +60% one-month spike is detected | ✅ PASS |
| U-039 | `test_detects_injected_down_spike` | Injected -50% one-month dip is detected | ✅ PASS |
| U-040 | `test_ignores_persistent_level_shift` | A permanent +70% step is not a spike | ✅ PASS |
| U-041 | `test_clean_series_has_no_spikes` | Smooth noisy series flags (almost) nothing | ✅ PASS |
| U-042 | `test_perfectly_smooth_series_spike_still_detected` | Edge case: zero-variance series (MAD=0) must not hide a spike | ✅ PASS |
| U-043 | `test_constant_series_no_error` | Constant series: no crash, no flags | ✅ PASS |
| U-044 | `test_endpoints_never_flagged` | First/last points (missing a neighbour) are never flagged | ✅ PASS |
| U-045 | `test_two_adjacent_high_points_not_spike` | Two consecutive high months are a mini-regime, not an isolated glitch | ✅ PASS |
| U-046 | `test_threshold_monotonic` | Raising the z-threshold never flags more points | ✅ PASS |
| U-047 | `test_returns_aligned_index` | Output shares the input index | ✅ PASS |

### C. Forecasting functions (baselines, ETS, ARIMA, GBM)

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-048 | `test_output_length[f_naive-1]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-049 | `test_output_length[f_naive-6]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-050 | `test_output_length[f_naive-12]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-051 | `test_output_length[f_naive-24]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-052 | `test_output_length[f_snaive-1]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-053 | `test_output_length[f_snaive-6]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-054 | `test_output_length[f_snaive-12]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-055 | `test_output_length[f_snaive-24]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-056 | `test_output_length[f_drift-1]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-057 | `test_output_length[f_drift-6]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-058 | `test_output_length[f_drift-12]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-059 | `test_output_length[f_drift-24]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-060 | `test_output_length[f_ses-1]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-061 | `test_output_length[f_ses-6]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-062 | `test_output_length[f_ses-12]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-063 | `test_output_length[f_ses-24]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-064 | `test_output_length[f_damped-1]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-065 | `test_output_length[f_damped-6]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-066 | `test_output_length[f_damped-12]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-067 | `test_output_length[f_damped-24]` | Each baseline returns exactly h forecasts | ✅ PASS |
| U-068 | `test_naive_value` | Naive = last observation | ✅ PASS |
| U-069 | `test_snaive_value` | Seasonal naive repeats last 12 values | ✅ PASS |
| U-070 | `test_snaive_wraps` | Seasonal naive wraps for h>12 | ✅ PASS |
| U-071 | `test_drift_exact_on_linear_series` | Drift reproduces a perfectly linear series | ✅ PASS |
| U-072 | `test_ses_constant_series` | SES of a constant series is that constant | ✅ PASS |
| U-073 | `test_ses_flat_forecast` | SES gives a flat multi-step forecast | ✅ PASS |
| U-074 | `test_ses_close_to_last_value` | On this series SES ~ last value (random-walk behaviour) | ✅ PASS |
| U-075 | `test_damped_finite` | Damped ETS finite | ✅ PASS |
| U-076 | `test_arima_forecast_finite` | ARIMA(0,1,1) finite | ✅ PASS |
| U-077 | `test_arima_with_drift_runs` | ARIMA with drift term runs | ✅ PASS |
| U-078 | `test_sarima_runs` | Seasonal SARIMA runs and is finite | ✅ PASS |
| U-079 | `test_gbm_length_and_finite` | GBM recursive forecast is finite and h long | ✅ PASS |
| U-080 | `test_gbm_deterministic` | GBM is reproducible (fixed random_state) | ✅ PASS |
| U-081 | `test_gbm_reasonable_range` | GBM forecast stays within +-50% of last price (no explosion) | ✅ PASS |
| U-082 | `test_forecasts_positive_after_exp` | Back-transformed forecasts are positive (log model cannot go negative) | ✅ PASS |
| U-083 | `test_functions_do_not_mutate_input` | Forecast functions do not modify the training series | ✅ PASS |
| U-084 | `test_candidate_registry` | 11 candidate models were compared | ✅ PASS |

### D. Evaluation metrics

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-085 | `test_perfect_forecast_zero_error` | Perfect forecast -> all errors 0 | ✅ PASS |
| U-086 | `test_known_mae` | MAE known case = 15 | ✅ PASS |
| U-087 | `test_known_rmse` | RMSE known case = sqrt(250) | ✅ PASS |
| U-088 | `test_known_mape` | MAPE known case = 10% | ✅ PASS |
| U-089 | `test_known_smape` | sMAPE known case | ✅ PASS |
| U-090 | `test_known_mase` | MASE = MAE / scale | ✅ PASS |
| U-091 | `test_rmse_ge_mae` | RMSE >= MAE always | ✅ PASS |
| U-092 | `test_metrics_nonnegative` | All metrics non-negative | ✅ PASS |
| U-093 | `test_symmetry_of_absolute_errors` | MAE same for over- and under-forecast of equal size | ✅ PASS |
| U-094 | `test_mape_asymmetric_property` | MAPE penalises over-forecast less than same-size under-forecast ratio base (documented property) | ✅ PASS |
| U-095 | `test_accepts_series` | Works with pandas Series input | ✅ PASS |
| U-096 | `test_returns_five_keys` | Returns MAE, RMSE, MAPE, sMAPE, MASE | ✅ PASS |
| U-097 | `test_scale_inverse_for_mase` | Doubling scale halves MASE | ✅ PASS |

### E. Rolling-origin cross-validation

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-098 | `test_origin_count` | 20 rolling origins | ✅ PASS |
| U-099 | `test_origin_bounds` | First origin Jan-2015 (idx 120); last leaves a full 12-month test window | ✅ PASS |
| U-100 | `test_origin_spacing` | Origins spaced 6 months | ✅ PASS |
| U-101 | `test_horizon_is_12` | Forecast horizon constant H = 12 (brief: next 12 months) | ✅ PASS |
| U-102 | `test_no_leakage_train_ends_before_test` | Training window passed to the model is strictly before the test window | ✅ PASS |
| U-103 | `test_cv_frame_shape` | CV result: 20 rows x 6 columns | ✅ PASS |
| U-104 | `test_stored_forecast_length` | Every stored forecast has H points | ✅ PASS |
| U-105 | `test_failure_falls_back_to_naive` | A model that raises falls back to naive instead of crashing the CV | ✅ PASS |
| U-106 | `test_cv_naive_equals_manual` | CV MAE for naive equals manual calculation on fold 1 | ✅ PASS |
| U-107 | `test_cv_metrics_nonnegative` | All CV fold metrics >= 0 | ✅ PASS |
| U-108 | `test_cv_has_all_candidates` | CV evaluated every candidate | ✅ PASS |
| U-109 | `test_tune_test_origins_disjoint` | Tuning origins and untouched test origins do not overlap | ✅ PASS |
| U-110 | `test_tuning_precedes_test` | All tuning origins are earlier than the untouched test origins (no look-ahead tuning) | ✅ PASS |

### F. Model selection & fine-tuning

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-111 | `test_summary_sorted_by_mape` | Comparison table sorted ascending by MAPE | ✅ PASS |
| U-112 | `test_ses_or_naive_best_baseline` | SES/Naive top the 11-model table | ✅ PASS |
| U-113 | `test_seasonal_naive_worst` | Seasonal naive is worst -> no seasonality to exploit | ✅ PASS |
| U-114 | `test_sarima_not_better_than_ses` | Seasonal SARIMA does not beat SES | ✅ PASS |
| U-115 | `test_arima_grid_size` | ARIMA grid: p,q in 0..3 x 2 trend options minus the empty model = 31 | ✅ PASS |
| U-116 | `test_arima_grid_sorted` | ARIMA grid sorted by MAPE | ✅ PASS |
| U-117 | `test_best_arima_is_grid_top` | Chosen ARIMA order = top of grid | ✅ PASS |
| U-118 | `test_gbm_grid_size` | GBM grid: 3 x 3 x 2 = 18 | ✅ PASS |
| U-119 | `test_gbm_grid_sorted` | GBM grid sorted | ✅ PASS |
| U-120 | `test_tuned_models_present` | Tuned model set includes naive, SES, damped, ARIMA, GBM, ensemble | ✅ PASS |
| U-121 | `test_ses_best_on_untouched_origins` | On the 8 untouched origins SES (or identical Naive) beats ARIMA, GBM and the ensemble | ✅ PASS |
| U-122 | `test_tuning_does_not_beat_naive_overall` | Tuned ARIMA/GBM do not beat naive across all 20 origins (supports parsimony) | ✅ PASS |
| U-123 | `test_by_horizon_error_grows` | Forecast error increases with horizon | ✅ PASS |
| U-124 | `test_dm_test_returns_t_and_p` | Diebold-Mariano helper returns finite t and p in [0,1] | ✅ PASS |
| U-125 | `test_dm_arima_worse_than_naive` | DM statistic positive (worse) for ARIMA vs Naive | ✅ PASS |

### G. Train vs test hold-out, residuals, robustness

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-126 | `test_split_date` | Split at Sep-2024 | ✅ PASS |
| U-127 | `test_train_test_sizes` | Train 237 months, test 12 months | ✅ PASS |
| U-128 | `test_test_follows_train` | Test starts right after train | ✅ PASS |
| U-129 | `test_alpha_is_one` | SES alpha fitted ~1 (random walk) | ✅ PASS |
| U-130 | `test_train_and_test_rows` | Report has Train and Test rows | ✅ PASS |
| U-131 | `test_train_error_lower_than_test` | 1-step in-sample error < 12-month-ahead error (as expected) | ✅ PASS |
| U-132 | `test_test_mape_value` | Hold-out MAPE ~9.1% | ✅ PASS |
| U-133 | `test_train_mape_value` | Train MAPE ~4.7% | ✅ PASS |
| U-134 | `test_competitor_table_complete` | Hold-out comparison includes 6 models | ✅ PASS |
| U-135 | `test_seasonal_worse_on_holdout` | Seasonal SARIMA clearly worse than SES on hold-out | ✅ PASS |
| U-136 | `test_nonseasonal_models_within_noise` | Non-seasonal models within 5% of each other on hold-out | ✅ PASS |
| U-137 | `test_residual_ljung_box_white` | Residuals show no autocorrelation (Ljung-Box p>0.05 at lags 6,12,24) | ✅ PASS |
| U-138 | `test_residuals_fat_tailed` | Residual excess kurtosis is large -> justifies empirical intervals | ✅ PASS |
| U-139 | `test_cleaning_robustness` | MAPE with/without cleaning differ by < 1pp (conclusions not sensitive) | ✅ PASS |

### H. 12-month forecast & intervals

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-140 | `test_twelve_rows` | Forecast has 12 rows | ✅ PASS |
| U-141 | `test_forecast_start_month` | First forecast month Oct-2025 | ✅ PASS |
| U-142 | `test_forecast_end_month` | Last forecast month Sep-2026 | ✅ PASS |
| U-143 | `test_forecast_contiguous` | Forecast months contiguous | ✅ PASS |
| U-144 | `test_forecast_positive` | All forecast & interval values positive | ✅ PASS |
| U-145 | `test_forecast_within_80` | lo_80 < forecast < hi_80 | ✅ PASS |
| U-146 | `test_80_inside_95` | 80% band nested in 95% band | ✅ PASS |
| U-147 | `test_intervals_widen_with_horizon` | Band width strictly increases with horizon | ✅ PASS |
| U-148 | `test_stress_wider_than_base` | Stress band at least as wide as base 80% | ✅ PASS |
| U-149 | `test_vol_ratio_bounds` | Volatility scaler clipped to [1, 2] | ✅ PASS |
| U-150 | `test_vol_ratio_value` | Recent volatility ~1.8x history | ✅ PASS |
| U-151 | `test_quantiles_ordered` | q2.5 < q10 < q50 < q90 < q97.5 | ✅ PASS |
| U-152 | `test_median_quantile_near_zero` | Median standardised error ~0 (unbiased centre) | ✅ PASS |
| U-153 | `test_pooled_error_count` | 240 pooled standardised errors (20 origins x 12) | ✅ PASS |
| U-154 | `test_80pct_empirical_coverage` | Empirical coverage of the 80% band in CV ~ 80% | ✅ PASS |
| U-155 | `test_central_forecast_near_last_price` | Central forecast within 2% of last observed price (random-walk logic) | ✅ PASS |
| U-156 | `test_forecast_csv_written` | forecast_next_12_months.csv written with 12 rows | ✅ PASS |
| U-157 | `test_forecast_csv_matches_frame` | CSV values equal in-memory forecast | ✅ PASS |
| U-158 | `test_base_forecast_flat` | SES base path is flat on log scale | ✅ PASS |
| U-159 | `test_hist_move_probabilities_sum` | Rise/fall/stable probabilities sum to 100% | ✅ PASS |
| U-160 | `test_hist_move_value` | P(rise>10% in 12m) ~41% | ✅ PASS |

### I. Model artifact & predict()

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-161 | `test_artifact_keys` | Artifact has all keys needed by the API | ✅ PASS |
| U-162 | `test_artifact_version` | Version string set | ✅ PASS |
| U-163 | `test_artifact_last_date` | last_date = Sep 2025 | ✅ PASS |
| U-164 | `test_artifact_rows` | Trained on 249 rows | ✅ PASS |
| U-165 | `test_artifact_level_log` | level_log ~ log(15750) | ✅ PASS |
| U-166 | `test_joblib_roundtrip` | joblib file reloads to the same dict | ✅ PASS |
| U-167 | `test_json_artifact_valid` | price_model.json is valid JSON identical to artifact | ✅ PASS |
| U-168 | `test_predict_default_horizon` | predict() default -> 12 rows with required columns | ✅ PASS |
| U-169 | `test_predict_horizon[1]` | predict(h) returns h rows | ✅ PASS |
| U-170 | `test_predict_horizon[3]` | predict(h) returns h rows | ✅ PASS |
| U-171 | `test_predict_horizon[12]` | predict(h) returns h rows | ✅ PASS |
| U-172 | `test_predict_horizon[24]` | predict(h) returns h rows | ✅ PASS |
| U-173 | `test_predict_matches_notebook_forecast` | predict() equals the notebook forecast table | ✅ PASS |
| U-174 | `test_predict_bands_match` | predict() 80% band equals notebook band | ✅ PASS |
| U-175 | `test_predict_months_format` | Month strings are YYYY-MM | ✅ PASS |
| U-176 | `test_predict_accepts_explicit_artifact` | predict(art=...) uses supplied artifact | ✅ PASS |

### J. Monitoring helpers (PSI, rolling MAPE)

| ID | Test | What it verifies | Result |
|---|---|---|---|
| U-177 | `test_psi_identical_zero` | PSI of identical samples = 0 | ✅ PASS |
| U-178 | `test_psi_shift_large` | PSI flags a 3-sigma mean shift as major (>0.25) | ✅ PASS |
| U-179 | `test_psi_small_shift_small` | Same-distribution resample has PSI < 0.1 | ✅ PASS |
| U-180 | `test_psi_nonnegative` | PSI >= 0 | ✅ PASS |
| U-181 | `test_psi_on_data_flags_drift` | PSI(last 24m vs history) > 0.25 -> drift flagged | ✅ PASS |
| U-182 | `test_monitor_frame_columns` | Monitoring frame has actual, ses, naive, ape, rolling MAPE, alert | ✅ PASS |
| U-183 | `test_monitor_length` | Walk-forward produced N-1-120 = 128 monthly rows | ✅ PASS |
| U-184 | `test_ape_nonnegative` | Absolute percentage errors >= 0 | ✅ PASS |
| U-185 | `test_rolling_mape_warmup` | Rolling MAPE NaN for first 11 months | ✅ PASS |
| U-186 | `test_alert_boolean` | Alert column boolean | ✅ PASS |
| U-187 | `test_ses_monitor_equals_naive` | 1-step SES ~ naive (alpha=1) in walk-forward | ✅ PASS |
