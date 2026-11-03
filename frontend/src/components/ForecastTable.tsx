import type { ForecastPoint } from "../types";
import { fmtMonth, fmtPrice, toCsv } from "../format";

export function downloadCsv(rows: ForecastPoint[]) {
  const csv = toCsv(rows.map(r => ({ ...r })) as unknown as Record<string, string | number>[]);
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  const a = document.createElement("a"); a.href = url; a.download = "forecast.csv"; a.click(); URL.revokeObjectURL(url);
}

export default function ForecastTable({ rows, stress }: { rows: ForecastPoint[]; stress: boolean }) {
  return (
    <section>
      <div className="row-between"><h2>Forecast table</h2><button className="btn btn-outline" onClick={() => downloadCsv(rows)}>Download CSV</button></div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Month</th><th>Forecast</th><th>{stress ? "Low (stress 80%)" : "Low (80%)"}</th><th>{stress ? "High (stress 80%)" : "High (80%)"}</th><th>Low (95%)</th><th>High (95%)</th></tr></thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.month}>
                <td>{fmtMonth(r.month)}</td><td><strong>{fmtPrice(r.forecast)}</strong></td>
                <td>{fmtPrice(stress ? r.lo_80_stress : r.lo_80)}</td><td>{fmtPrice(stress ? r.hi_80_stress : r.hi_80)}</td>
                <td>{fmtPrice(r.lo_95)}</td><td>{fmtPrice(r.hi_95)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
