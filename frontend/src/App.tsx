import { useMemo, useState } from "react";
import { useForecastData } from "./useForecastData";
import KpiCards from "./components/KpiCards";
import ForecastChart, { buildChartRows } from "./components/ForecastChart";
import ForecastTable from "./components/ForecastTable";
import BudgetPlanner from "./components/BudgetPlanner";
import Way2Dashboard from "./components/Way2Dashboard";
import { fmtMonth } from "./format";

const HORIZONS = [3, 6, 12, 24];
const RANGES: { label: string; months: number }[] = [{ label: "3 years", months: 36 }, { label: "5 years", months: 60 }, { label: "10 years", months: 120 }, { label: "All", months: 600 }];
const TABS = [{ id: "forecast", label: "Price Forecast" }, { id: "way2", label: "Way2 Ecosystem" }] as const;

export default function App() {
  const [tab, setTab] = useState<(typeof TABS)[number]["id"]>("forecast");
  const [horizon, setHorizon] = useState(12);
  const [range, setRange] = useState(60);
  const [stress, setStress] = useState(true);
  const [show95, setShow95] = useState(false);
  const { loading, error, forecast, history, model, retry } = useForecastData(horizon);

  const rows = useMemo(() => (forecast ? buildChartRows(history, forecast.forecast, range) : []), [forecast, history, range]);

  return (
    <main>
      <nav className="tabs" aria-label="Sections">
        {TABS.map(t => (
          <button key={t.id} type="button" className={`tab${tab === t.id ? " active" : ""}`}
            aria-pressed={tab === t.id} onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </nav>

      {tab === "forecast" && (
        <>
          <header>
            <div>
              <h1>Average Monthly Price Forecast</h1>
              <p className="muted">{model ? `Data to ${fmtMonth(model.last_date)} · model ${model.model_version}` : "Loading…"}</p>
            </div>
            <div className="controls">
              <label>Horizon
                <select value={horizon} onChange={e => setHorizon(Number(e.target.value))} aria-label="Forecast horizon">
                  {HORIZONS.map(h => <option key={h} value={h}>{h} months</option>)}
                </select>
              </label>
              <label>History
                <select value={range} onChange={e => setRange(Number(e.target.value))} aria-label="History range">
                  {RANGES.map(r => <option key={r.months} value={r.months}>{r.label}</option>)}
                </select>
              </label>
              <label className="check"><input type="checkbox" checked={stress} onChange={e => setStress(e.target.checked)} /> Stress band</label>
              <label className="check"><input type="checkbox" checked={show95} onChange={e => setShow95(e.target.checked)} /> 95% band</label>
            </div>
          </header>

          {error && (
            <div role="alert" className="error">
              <p>{error}</p>
              <button className="btn btn-primary" onClick={retry}>Retry</button>
            </div>
          )}
          {loading && !error && <p role="status" className="muted">Loading forecast…</p>}

          {!error && forecast && model && !loading && (
            <>
              <KpiCards model={model} forecast={forecast.forecast} stress={stress} />
              <ForecastChart rows={rows} show95={show95} stress={stress} />
              <p className="note">
                The model predicts a <strong>central level and a risk band</strong>, not a direction. Prices in this series move in sudden regime shifts, so plan on the band.
                The stress band widens the interval by recent volatility ({model.vol_scale.toFixed(1)}× history).
              </p>
              <div className="grid">
                <ForecastTable rows={forecast.forecast} stress={stress} />
                <BudgetPlanner rows={forecast.forecast} stress={stress} />
              </div>
            </>
          )}
        </>
      )}

      {tab === "way2" && <Way2Dashboard />}
    </main>
  );
}
