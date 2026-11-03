import type { ForecastPoint, ForecastResponse, HistoryPoint, ModelInfo } from "../types";

export const model: ModelInfo = { model_version: "2025-09-v1", model: "SES_log", alpha: 1, cv_mape: 14.79, vol_scale: 1.78, last_date: "2025-09", trained_on_rows: 249, last_price: 15750 };

export function fcPoints(n: number): ForecastPoint[] {
  return Array.from({ length: n }, (_, i) => {
    const m = i + 1, month = `${2025 + Math.floor((8 + m) / 12)}-${String(((8 + m) % 12) + 1).padStart(2, "0")}`, f = 15800 + i * 10;
    return { month, forecast: f, lo_80: f - 1000 - i * 100, hi_80: f + 1600 + i * 300, lo_95: f - 2500 - i * 200, hi_95: f + 4000 + i * 700, lo_80_stress: f - 1700 - i * 150, hi_80_stress: f + 2800 + i * 500 };
  });
}
export const forecastResp = (n = 12): ForecastResponse => ({ model_version: "2025-09-v1", horizon: n, forecast: fcPoints(n) });
export const history: HistoryPoint[] = Array.from({ length: 80 }, (_, i) => ({ month: `${2019 + Math.floor((i + 0) / 12)}-${String((i % 12) + 1).padStart(2, "0")}`, price: 8000 + i * 90 }));

/** fetch mock keyed by path; override with a function or Response status */
export function mockFetch(overrides: Record<string, unknown> = {}) {
  return vi.fn(async (url: string, _init?: RequestInit) => {
    const u = String(url);
    const hit = Object.keys(overrides).find(k => u.includes(k));
    if (hit) { const o = overrides[hit]; if (typeof o === "number") return new Response("{}", { status: o }); if (o instanceof Error) throw o; return new Response(JSON.stringify(o)); }
    if (u.includes("/v1/forecast")) { const h = Number(new URL(u).searchParams.get("horizon")); return new Response(JSON.stringify(forecastResp(h))); }
    if (u.includes("/v1/history")) return new Response(JSON.stringify({ points: history }));
    if (u.includes("/v1/model")) return new Response(JSON.stringify(model));
    return new Response("{}", { status: 404 });
  });
}
