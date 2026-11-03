"""Price-forecast API (FastAPI).  Serves the model artifact produced by price_forecast.ipynb.

Dev:  uvicorn backend.main:app --reload --port 8000        (from the project root)
Prod: put this behind the Django gateway (JWT auth, rate limits) as described in notebook section 8;
      set REQUIRE_KEY=1 and SERVICE_KEY=... so only Django can call it.
"""
import os, pathlib
import joblib, numpy as np, pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = pathlib.Path(os.environ.get("MODEL_PATH", ROOT / "price_model.joblib"))
DATA_PATH = pathlib.Path(os.environ.get("DATA_PATH", ROOT / "price_data.csv"))

app = FastAPI(title="Price Forecast Service", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:4173,http://127.0.0.1:5173").split(","),
    allow_methods=["GET"], allow_headers=["*"],
)
STATE = {"art": joblib.load(MODEL_PATH)}


def auth(x_api_key: str | None = Header(default=None)):
    if os.environ.get("REQUIRE_KEY") == "1" and x_api_key != os.environ.get("SERVICE_KEY"):
        raise HTTPException(401, "invalid api key")


def _bands(art, horizon):
    h = np.arange(1, horizon + 1); sq = np.sqrt(h); q = art["quantiles"]; lv = art["level_log"]; vs = art.get("vol_scale", 1.0)
    months = pd.date_range(pd.Timestamp(art["last_date"]) + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    e = lambda z: np.round(np.exp(lv + sq * z))
    cols = {"forecast": e(q["0.5"]), "lo_80": e(q["0.1"]), "hi_80": e(q["0.9"]), "lo_95": e(q["0.025"]), "hi_95": e(q["0.975"]),
            "lo_80_stress": e(q["0.1"] * vs), "hi_80_stress": e(q["0.9"] * vs)}
    return [{"month": m.strftime("%Y-%m"), **{k: float(v[i]) for k, v in cols.items()}} for i, m in enumerate(months)]


@app.get("/health")
def health():
    return {"status": "ok", "model_version": STATE["art"]["version"]}


@app.get("/v1/model", dependencies=[Depends(auth)])
def model_info():
    a = STATE["art"]; hist = pd.read_csv(DATA_PATH)
    return {"model_version": a["version"], "model": a["model"], "alpha": a["alpha"], "cv_mape": a["cv_mape"], "vol_scale": a.get("vol_scale", 1.0),
            "last_date": a["last_date"][:7], "trained_on_rows": a["trained_on_rows"], "last_price": float(hist.avg_monthly_price.iloc[-1])}


@app.get("/v1/forecast", dependencies=[Depends(auth)])
def forecast(horizon: int = Query(12, ge=1, le=24)):
    return {"model_version": STATE["art"]["version"], "horizon": horizon, "forecast": _bands(STATE["art"], horizon)}


@app.get("/v1/history", dependencies=[Depends(auth)])
def history(months: int = Query(120, ge=6, le=600)):
    d = pd.read_csv(DATA_PATH, parse_dates=["date"]).tail(months)
    return {"points": [{"month": r.date.strftime("%Y-%m"), "price": float(r.avg_monthly_price)} for r in d.itertuples()]}


if __name__ == "__main__":      # lets you start it from ANY folder:  python3 /path/to/Assignment/backend/main.py
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
