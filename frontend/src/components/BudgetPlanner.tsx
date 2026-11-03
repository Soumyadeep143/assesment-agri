import { useState } from "react";
import type { ForecastPoint } from "../types";
import { fmtPrice } from "../format";

/** Turns the forecast into a purchasing budget: central case vs. upper-risk case (notebook section 5: "size budgets on the upper bound"). */
export default function BudgetPlanner({ rows, stress }: { rows: ForecastPoint[]; stress: boolean }) {
  const [volume, setVolume] = useState(100);
  const v = Number.isFinite(volume) && volume > 0 ? volume : 0;
  const central = rows.reduce((s, r) => s + r.forecast * v, 0);
  const upper = rows.reduce((s, r) => s + (stress ? r.hi_80_stress : r.hi_80) * v, 0);
  return (
    <section className="planner">
      <h2>Budget planner</h2>
      <label>Monthly purchase volume (units)
        <input type="number" min={0} value={volume} onChange={e => setVolume(Number(e.target.value))} aria-label="Monthly volume" />
      </label>
      <dl>
        <div><dt>Budget at central forecast ({rows.length} months)</dt><dd data-testid="budget-central">{fmtPrice(central)}</dd></div>
        <div><dt>Budget at upper 80% bound</dt><dd data-testid="budget-upper">{fmtPrice(upper)}</dd></div>
        <div><dt>Risk buffer to hold</dt><dd data-testid="budget-buffer">{fmtPrice(upper - central)}</dd></div>
      </dl>
      <p className="note">Illustrative only: assumes the same volume every month and that the price index applies per unit.</p>
    </section>
  );
}
