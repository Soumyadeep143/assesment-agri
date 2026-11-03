export interface ForecastPoint {
  month: string; forecast: number; lo_80: number; hi_80: number;
  lo_95: number; hi_95: number; lo_80_stress: number; hi_80_stress: number;
}
export interface ForecastResponse { model_version: string; horizon: number; forecast: ForecastPoint[]; }
export interface HistoryPoint { month: string; price: number; }
export interface HistoryResponse { points: HistoryPoint[]; }
export interface ModelInfo {
  model_version: string; model: string; alpha: number; cv_mape: number; vol_scale: number;
  last_date: string; trained_on_rows: number; last_price: number;
}
