import type { ForecastResponse, HistoryResponse, ModelInfo } from "./types";

export const API_URL: string = (import.meta.env?.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

/** Dev: no auth.  Prod (Django gateway): return { Authorization: `Bearer ${token}` } from your auth layer. */
export function authHeaders(): Record<string, string> {
  return {};
}

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); this.name = "ApiError"; }
}

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { headers: authHeaders(), signal });
  } catch (e) {
    if ((e as Error).name === "AbortError") throw e;
    throw new ApiError(0, "Cannot reach the forecast service. Is the API running?");
  }
  if (!res.ok) throw new ApiError(res.status, res.status === 422 ? "Invalid request parameters." : `Forecast service error (${res.status}).`);
  return (await res.json()) as T;
}

export const fetchForecast = (horizon: number, signal?: AbortSignal) => get<ForecastResponse>(`/v1/forecast?horizon=${horizon}`, signal);
export const fetchHistory = (months: number, signal?: AbortSignal) => get<HistoryResponse>(`/v1/history?months=${months}`, signal);
export const fetchModel = (signal?: AbortSignal) => get<ModelInfo>("/v1/model", signal);
