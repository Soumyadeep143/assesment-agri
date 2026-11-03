# Breakdown Summary Report — Average Monthly Price Forecasting

**Deliverable:** `price_forecast.ipynb` · **Data used:** `price_data.csv` only (249 monthly rows, Jan-2005 → Sep-2025) · **Forecast:** Oct-2025 → Sep-2026

Companion reports: [`UNIT_TEST_REPORT.md`](UNIT_TEST_REPORT.md) (187 cases) · [`INTEGRATION_TEST_REPORT.md`](INTEGRATION_TEST_REPORT.md) (118 cases)

---

## 1. Verdict at a glance

| Item | Result |
|---|---|
| Unit tests | **187 / 187 passed** (required ≥ 100) |
| Integration tests | **118 / 118 passed** (required ≥ 50) |
| Fault-detection check | Deliberately broken copy of the notebook (horizon 12→6, spike threshold 3.5→0.5, naive off by one month, MAE ×2) → **47 of 305 tests failed**, so the suite does detect faults |
| Business-case requirements | All technical requirements met; **3 submission steps are manual** (WhatsApp, e-mail, resume) and **contact details must be filled in** (section 5) |
| Honest limitation | Forecast accuracy is limited (12-month CV MAPE 14.8%). The series behaves like a random walk with regime shifts; this is a property of the data, reported openly, not hidden |

**What the tests do and don't prove.** They execute the notebook's *own* code cells in a sandbox and check behaviour, internal consistency, reproducibility, and that every number quoted in the narrative equals the computed number. They prove the notebook is *correct and consistent with the brief*. They do not prove the forecast will be accurate in the future, and the Django / Next.js / React Native snippets were checked for validity and logic but not run inside real Django/Node/Expo projects (details in section 6).

---

## 2. Feature-by-feature breakdown (what, why, evidence)

| # | Feature | What it does | Why I did it | Verified by |
|---|---|---|---|---|
| F1 | Data loading & schema checks | Reads `price_data.csv`, checks columns, dtypes, ISO dates, nulls, duplicates, ≤0 prices, calendar gaps | The data dictionary defines two fields; any model on bad input is meaningless. Checks run first so problems surface before modelling | Unit A (12), Integration §2 |
| F2 | Monthly index + gap interpolation | `asfreq("MS")` + time interpolation | Time-series libraries need a regular index. No gaps exist today (0 filled) but the step protects future data refreshes | Unit B |
| F3 | Log transform | Models `log(price)` | Price moves are proportional (a 500 move matters more at 5,000 than at 15,000); stabilises variance; makes forecasts positive by construction | Unit C, B |
| F4 | **Isolated-spike detector** (`detect_spikes`) | Flags a month only if it is far from *both* neighbours, the neighbours agree with each other, and it is a local extreme (robust MAD z-score > 3.5). Replaces by interpolation | Brief asks to handle outliers. A naive z-score would also delete real regime shifts (my first version flagged Nov-2013 and Dec-2023 — fixed). Result: 5 spikes replaced | Unit B (35 incl. 10 synthetic spike/shift/edge cases) |
| F5 | Level-shift retention | Large *persistent* jumps (Nov-2013, Jun-2021, Dec-2023) are reported but kept | They are real information; deleting them would hide the very risk being forecast | Unit B, Integration §2 |
| F6 | Stale-value flag | 9 consecutive repeated prices flagged, kept | Likely carried-forward quotes; no ground truth to replace them | Unit B |
| F7 | Data-quality caveat (replayed history) | Jun-2021→ values exactly equal Oct-2007→ values (12/12) | Possible back-fill; I cannot verify the source so I disclosed it and tested sensitivity instead of silently changing data | Unit B, Integration §4 |
| F8 | EDA: STL, ADF/KPSS, ACF/PACF, month test | Decomposition, stationarity, autocorrelation | Decide the model family *from evidence*: non-stationary in levels (d=1), seasonal strength ≈ 0, almost no autocorrelation in returns | Integration §2 (R04–R05) |
| F9 | Candidate model set (11 models) | Naïve, seasonal naïve, drift, SES, damped ETS, ARIMA ×4, SARIMA, GBM on lags | Brief allows "any" method: I compared statistical and ML families rather than assuming one. LSTM consciously excluded (≈250 points, no non-linear structure) and documented | Unit C (37), Integration §2 |
| F10 | Metrics: MAE, RMSE, MAPE, sMAPE, MASE | Computed on original price scale | Brief asks for "appropriate evaluation metrics". MAPE is business-readable; MASE shows value vs naïve; RMSE penalises big misses | Unit D (13, hand-computed cases) |
| F11 | **Rolling-origin CV** | 20 expanding-window origins (Jan-2015→), 12-month horizon, 240 forecasts | One split is unreliable on a series with level shifts. Brief says evaluate on *future months*: each fold trains only on the past (spy test proves no leakage) | Unit E (13) |
| F12 | Fine-tuning | ARIMA grid (31 combos) + GBM grid (18) tuned on the **first 12 origins only**; last 8 origins untouched | Prevents optimistic tuning. Result: tuning did **not** beat naïve out-of-sample — reported honestly | Unit F (15) |
| F13 | Diebold–Mariano test, error-by-horizon | Statistical comparison vs naïve; error growth over 12 months | "Looks better" isn't evidence; shows complex models are significantly *worse* than naïve and uncertainty grows with horizon | Unit F |
| F14 | Final hold-out (train vs test) | Train to Sep-2024, test Oct-2024→Sep-2025 | Brief explicitly asks for *training and predictive performance*. Train 1-step MAPE 4.7% vs test 12-month 9.1% | Unit G (14) |
| F15 | Model selection: SES (α = 1 → log random walk) | Chosen on CV + parsimony | Lowest/equal-lowest CV error; more complex models fit tuning data better but lose out-of-sample (over-fit); simple, explainable, cheap to deploy | Unit F/G, Integration §3 |
| F16 | Residual diagnostics | Ljung-Box, skew/kurtosis, Q-Q | Confirms no leftover autocorrelation; fat tails justify empirical (not Gaussian) intervals | Unit G |
| F17 | Robustness checks | Raw vs cleaned data; excluding the suspicious stretch | Shows conclusions don't depend on my cleaning choices or the data caveat | Unit G, Integration §3 |
| F18 | Empirical prediction intervals | 80%/95% bands from 240 pooled CV errors scaled by √h | Gaussian formulas under-state risk on fat-tailed series; empirical coverage in CV ≈ 80% | Unit H (21) |
| F19 | Volatility-adjusted "stress" band | Scales band by recent/historical volatility (1.8×, capped 2) | Recent volatility doubled (PSI 1.19), so the history-calibrated band is probably too narrow — added after I noticed this | Unit H, Integration §3 |
| F20 | Historical move probabilities | P(>10% rise/fall in 12 months): 41% / 31% | Converts a flat forecast into decision-useful odds | Unit H |
| F21 | Model artifact + `predict()` | `price_model.joblib/json` (α, level, quantiles, version) | The deployment sections need something concrete; tiny, versioned, reloadable | Unit I (16), Integration §3/5 |
| F22 | Q4 Business actions | Table by scenario (rise / fall / flat-uncertain) + decision-rule process | Because the forecast is a band, not a direction, actions are robust-to-uncertainty (laddered buying, hedging, index pricing) | Integration §2, §6 |
| F23 | Q5 Effectiveness measurement | KPIs, control group/DiD, synthetic baseline, bootstrap, net benefit | Separates "market moved our way" from "our decisions worked" | Integration §2, §6 |
| F24 | Q6 Django deployment | Architecture, project layout, DRF endpoint, Celery, hardening, CI tests | Brief asks for Django deployment; includes model-regression gate | Integration §5 (syntax, logic via stubbed settings) |
| F25 | Q7 Django + FastAPI | FastAPI inference service, Django proxy client with cache/timeout | Separates business logic (Django) from fast inference (FastAPI) | Integration §5b — **code executed with TestClient (19 cases)** |
| F26 | Q8 Next.js & React Native | Server-side token handling, TanStack Query, SecureStore, charts with uncertainty band | Tokens stay off browser JS; same contract for web and mobile | Integration §5 (syntax/bracket checks only) |
| F27 | Q9 Monitoring | Service/data/model monitoring, PSI, rolling MAPE, alert rules, champion–challenger, rollback; **simulated walk-forward demo** | Regime-switching series fail via shifts; alerts + human review + rollback | Unit J, Integration §6 |
| F28 | Conclusion & limitations | States accuracy cap, data caveat, upgrade path | Honest scope for reviewers | Integration §1 |
| F29 | Deliverable files | notebook, forecast CSV, model artifact | Reproducible, shippable | Integration §1 |
| F30 | Automated test suite | `tests/` — 305 cases + report generator | Requested; also catches regressions | This report |

---

## 3. Word-by-word requirement traceability

Status: ✅ Met · 🟡 Met with caveat · 🧍 Manual (you must do it)

### Introduction & submission
| # | Words in the brief | Status | Evidence / note |
|---|---|---|---|
| 1 | "come up with a solution for the provided business case" | ✅ | Whole notebook |
| 2 | "Submit your solution in Jupyter Notebook (.ipynb) format" | ✅ | `price_forecast.ipynb`; nbformat-validated, kernel Python 3, executed with saved outputs (Integration §1) |
| 3 | "Send a copy via WhatsApp to +91 9449004956" | 🧍 | Your action |
| 4 | "Email a copy to way2agriintelai@gmail.com, and include your name and contact number" | 🧍 | Your action |
| 5 | "Your Updated Resume" | 🧍 | I don't have it; attach it |
| 6 | "Failure to include contact details (phone and email) will lead to rejection" | 🟡 | Notebook header has Name/Phone/Email fields **with placeholders `[YOUR NAME]` etc. — fill them in**. A test deliberately flags this |

### Business context
| # | Words in the brief | Status | Evidence / note |
|---|---|---|---|
| 7 | "develop a model to forecast **average monthly prices**" | ✅ | Target `avg_monthly_price` |
| 8 | "**for the next 12 months**" | ✅ | 12 rows, Oct-2025→Sep-2026, starts the month after the last observation |
| 9 | "using the provided dataset … CSV … historical monthly prices" | ✅ | Only `price_data.csv` read; test scans code for any other data source/URL → none. (Your instruction "use only the mentioned dataset" is honoured) |
| 10 | "any suitable machine learning, deep learning, statistical time series … method" | ✅ | Statistical + ML compared. 🟡 Deep learning not built; deliberately excluded and justified in the notebook |
| 11 | "trained on historical data" | ✅ | Expanding windows on past data only (no-leakage test) |
| 12 | "evaluated for both training and predictive performance on future months" | ✅ | §3.2: train 1-step vs 12-month-ahead test, plus 20-origin CV |
| 13 | "dedicate sufficient time to fine-tuning" | ✅ 🟡 | ARIMA and GBM grids tuned; tuning did not improve on naïve out-of-sample (reported) |
| 14 | "interpreting the results" | ✅ | §3.3 "Why SES", "Honest reading", residual notes, key-results table |

### Data dictionary & source
| # | Words | Status | Evidence |
|---|---|---|---|
| 15 | `date` — ISO 8601 YYYY-MM-DD | ✅ | Tested: all 249 dates are 10-char ISO, day = 01 |
| 16 | `avg_monthly_price` — average monthly price | ✅ | Numeric, positive |
| 17 | Data Source link | ✅ | Downloaded and used as `price_data.csv` |

### Candidate expectations (the nine questions)
| # | Words in the brief | Status | Where |
|---|---|---|---|
| Q1 | "Perform data cleaning, including handling **missing values**, **outliers**, and **anomalies**" | ✅ | §1 (no nulls found; spikes treated; level shifts/stale/replay flagged) |
| Q2 | "Describe your price prediction model **in detail** and **explain the reasons** for selecting this model" | ✅ | §2, §3.3 |
| Q3 | "Demonstrate the performance of the model using **appropriate evaluation metrics**" | ✅ | §3 (MAE, RMSE, MAPE, sMAPE, MASE; CV + hold-out; DM test) |
| Q4 | "Suggest **actions a company could take** to respond to predicted price changes" | ✅ | §5 |
| Q5 | "Assuming these actions have been implemented, **how would you determine if they are effective**" | ✅ | §6 |
| Q6 | "Explain how you would **deploy the model to production using Django**" | ✅ | §7 |
| Q7 | "**integrate the model into a Django- and FastAPI-based web application** for **real-time predictions**" | ✅ | §8 (FastAPI snippet executed in tests) |
| Q8 | "integrate the APIs … into frontend frameworks such as **Next.js** and **React Native**" | ✅ 🟡 | §9; snippets syntax-checked, not run in real Next/Expo projects |
| Q9 | "**monitor** the model in production, including **tracking performance**, **handling model drift**, and **updating the model**" | ✅ | §10 + runnable monitoring demo (PSI, rolling MAPE, alerts) |

---

## 4. Defects and issues found (and what I did)

| # | Found | When | Action |
|---|---|---|---|
| D1 | First spike rule flagged real regime shifts (Nov-2013, Dec-2023) as outliers | Build | Added "neighbours must agree" condition; shifts now kept |
| D2 | Text claimed month-of-year test was "not significant" but p = 0.023 | Build | Reworded to the true result and explained why seasonality still has no forecasting value |
| D3 | Initial plan implied complex model might win; CV showed SES/naïve wins | Build | Selected on evidence; documented that α = 1 means a random walk |
| D4 | History-calibrated intervals looked too narrow vs. doubled recent volatility | Build | Added the volatility-adjusted stress band |
| D5 | **`detect_spikes` could silently miss a spike when the robust spread (MAD) is exactly 0** (perfectly smooth series) | Test design | Fixed with a floor (`max(mad, 1e-9)`); regression test added; notebook re-executed |
| D6 | My own test expected ≥ 6 Python snippets; notebook has 4 | First test run (304/305) | Test assumption was wrong, not the notebook — corrected to ≥ 4 |
| D7 | One of my tests (`alert needs baseline`) had a branch that always passed | Review | Rewritten to check the real code |

## 5. Before you submit — your checklist
1. Replace `[YOUR NAME]`, `[YOUR PHONE]`, `[YOUR EMAIL]` in the first notebook cell.
2. Send `price_forecast.ipynb` to **+91 9449004956** (WhatsApp) and **way2agriintelai@gmail.com** (e-mail with name + phone).
3. Attach your updated resume.
4. Optional: re-run the notebook after editing (≈2 minutes) so saved outputs stay current.

## 6. Limitations and what remains unverified (stated plainly)
- **Forecast accuracy is capped.** One univariate series with regime shifts and no drivers: 12-month CV MAPE 14.8%; 21.4% on the most recent 8 origins. The forecast is a central estimate plus a risk band, not a directional call.
- **Tests verify code and consistency, not future accuracy.** Several tests lock current results (e.g. MAPE 14.8%); if data or code changes they will fail by design.
- **React (added after the first report):** a real React + TypeScript dashboard (`frontend/`) and the FastAPI backend (`backend/main.py`) were built and run together: `tsc` clean, 45 UI tests + 17 backend tests pass, production build succeeds, and the page was loaded in headless Chrome against the live API and showed the notebook's exact numbers. The UI tests use a mocked `fetch`; the live check was a screenshot, not an automated browser test.
- **Django, Next.js, React Native snippets:** still only checked for valid syntax; Django service logic exercised with stubbed settings; FastAPI actually executed. They were **not** run inside a real Django project, a Next.js build or an Expo app.
- **Data caveat (F7)** remains unresolved until the data owner confirms the source of the Jun-2021→Oct-2023 values.
- **Monitoring demo** alerts frequently (52 months) because the series is regime-switching; the notebook explains this and recommends a robust baseline and persistence rules before acting on alerts.
- **Pass rate of 100% on first-class checks is partly by construction** (many tests lock behaviour I wrote). That is why the mutation check matters: when I broke the code on purpose, 47 tests failed.

## 7. How to re-run everything
```bash
cd /Users/vidipghosh/Desktop/Assignment
python -m pip install pandas numpy statsmodels scikit-learn matplotlib scipy nbformat joblib pytest fastapi httpx
python -m pytest                      # ~2.5 min: executes the notebook's code + 305 tests
python tests/gen_reports.py           # regenerates UNIT_/INTEGRATION_TEST_REPORT.md from tests/results.json
```
