import { useCallback, useEffect, useState } from "react";
import { fetchForecast, fetchHistory, fetchModel } from "./api";
import type { ForecastResponse, HistoryPoint, ModelInfo } from "./types";

export interface State {
  loading: boolean; error: string | null;
  forecast: ForecastResponse | null; history: HistoryPoint[]; model: ModelInfo | null;
}

export function useForecastData(horizon: number) {
  const [s, setS] = useState<State>({ loading: true, error: null, forecast: null, history: [], model: null });
  const [nonce, setNonce] = useState(0);
  const retry = useCallback(() => setNonce(n => n + 1), []);

  useEffect(() => {
    const ctl = new AbortController();
    setS(p => ({ ...p, loading: true, error: null }));
    Promise.all([fetchForecast(horizon, ctl.signal), fetchHistory(600, ctl.signal), fetchModel(ctl.signal)])
      .then(([forecast, h, model]) => setS({ loading: false, error: null, forecast, history: h.points, model }))
      .catch(e => { if ((e as Error).name !== "AbortError") setS(p => ({ ...p, loading: false, error: (e as Error).message })); });
    return () => ctl.abort();
  }, [horizon, nonce]);

  return { ...s, retry };
}
