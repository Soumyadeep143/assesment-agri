const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export const fmtPrice = (v: number): string => Math.round(v).toLocaleString("en-IN");

/** "2025-10" -> "Oct 2025" */
export function fmtMonth(m: string): string {
  const [y, mo] = m.split("-").map(Number);
  if (!y || !mo || mo < 1 || mo > 12) return m;
  return `${MONTHS[mo - 1]} ${y}`;
}

export const fmtPct = (v: number, digits = 1): string => `${v >= 0 ? "+" : ""}${v.toFixed(digits)}%`;

export const pctChange = (from: number, to: number): number => (from === 0 ? 0 : (to / from - 1) * 100);

export function toCsv(rows: Record<string, string | number>[]): string {
  if (!rows.length) return "";
  const cols = Object.keys(rows[0]);
  return [cols.join(","), ...rows.map(r => cols.map(c => r[c]).join(","))].join("\n");
}
