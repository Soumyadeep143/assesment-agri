import type { ForecastPoint, ModelInfo } from "../types";
import { fmtMonth, fmtPct, fmtPrice, pctChange } from "../format";

export default function KpiCards({ model, forecast, stress }: { model: ModelInfo; forecast: ForecastPoint[]; stress: boolean }) {
  const last = forecast[forecast.length - 1];
  const lo = stress ? last.lo_80_stress : last.lo_80, hi = stress ? last.hi_80_stress : last.hi_80;
  const chg = pctChange(model.last_price, last.forecast);
  return (
    <section className="kpis" aria-label="Key figures">
      <div className="card"><span className="label">Last observed price ({fmtMonth(model.last_date)})</span><strong data-testid="kpi-last">{fmtPrice(model.last_price)}</strong></div>
      <div className="card"><span className="label">Central forecast, {fmtMonth(last.month)}</span><strong data-testid="kpi-forecast">{fmtPrice(last.forecast)}</strong>
        <span className="sub">{fmtPct(chg)} vs last price</span></div>
      <div className="card"><span className="label">{stress ? "Stress" : "Standard"} 80% range, {fmtMonth(last.month)}</span>
        <strong data-testid="kpi-range">{fmtPrice(lo)} – {fmtPrice(hi)}</strong><span className="sub">{fmtPct(pctChange(model.last_price, lo))} to {fmtPct(pctChange(model.last_price, hi))}</span></div>
      <div className="card"><span className="label">Back-test error (12-month MAPE)</span><strong data-testid="kpi-mape">{model.cv_mape.toFixed(1)}%</strong>
        <span className="sub">20 rolling origins</span></div>
    </section>
  );
}
