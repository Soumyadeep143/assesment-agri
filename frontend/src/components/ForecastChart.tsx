import { Area, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ForecastPoint, HistoryPoint } from "../types";
import { fmtMonth, fmtPrice } from "../format";

export interface ChartRow {
  month: string; price?: number; forecast?: number; band80?: [number, number]; band95?: [number, number]; stress?: [number, number];
}

export function buildChartRows(history: HistoryPoint[], forecast: ForecastPoint[], historyMonths: number): ChartRow[] {
  const h = history.slice(-historyMonths);
  const rows: ChartRow[] = h.map(p => ({ month: p.month, price: p.price }));
  if (rows.length) rows[rows.length - 1].forecast = rows[rows.length - 1].price;       // join the two lines
  forecast.forEach(f => rows.push({ month: f.month, forecast: f.forecast, band80: [f.lo_80, f.hi_80], band95: [f.lo_95, f.hi_95], stress: [f.lo_80_stress, f.hi_80_stress] }));
  return rows;
}

export default function ForecastChart({ rows, show95, stress }: { rows: ChartRow[]; show95: boolean; stress: boolean }) {
  return (
    <div className="chart" role="img" aria-label="Price history with 12-month forecast and uncertainty bands">
      <ResponsiveContainer width="100%" height={380}>
        <ComposedChart data={rows} margin={{ top: 10, right: 16, left: 4, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
          <XAxis dataKey="month" tickFormatter={fmtMonth} minTickGap={48} stroke="var(--muted)" />
          <YAxis tickFormatter={fmtPrice} stroke="var(--muted)" width={64} domain={["auto", "auto"]} />
          <Tooltip formatter={(v: unknown) => (Array.isArray(v) ? `${fmtPrice(v[0])} – ${fmtPrice(v[1])}` : fmtPrice(Number(v)))} labelFormatter={(l: unknown) => fmtMonth(String(l))} />
          <Legend />
          {show95 && <Area dataKey="band95" name="95% interval" stroke="none" fill="var(--band95)" isAnimationActive={false} />}
          <Area dataKey={stress ? "stress" : "band80"} name={stress ? "80% interval (stress)" : "80% interval"} stroke="none" fill="var(--band80)" isAnimationActive={false} />
          <Line dataKey="price" name="Actual" stroke="var(--actual)" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line dataKey="forecast" name="Forecast" stroke="var(--forecast)" strokeWidth={2.5} strokeDasharray="6 3" dot={false} isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
