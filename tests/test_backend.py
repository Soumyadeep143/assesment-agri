"""Tests for backend/main.py – the real API the React app calls."""
import pathlib, sys
import numpy as np, pandas as pd, pytest
from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.main import app  # noqa: E402

c = TestClient(app)
CSV = pd.read_csv(ROOT / "forecast_next_12_months.csv", index_col=0)


def test_health():
    """/health ok"""
    assert c.get("/health").json() == {"status": "ok", "model_version": "2025-09-v1"}

def test_forecast_matches_notebook_csv():
    """API forecast and all bands equal the notebook's saved forecast CSV (+/-1 rounding)"""
    j = c.get("/v1/forecast?horizon=12").json()["forecast"]
    for col in ["forecast", "lo_80", "hi_80", "lo_95", "hi_95", "lo_80_stress", "hi_80_stress"]:
        assert np.allclose([p[col] for p in j], CSV[col], atol=1.0), col

@pytest.mark.parametrize("h", [1, 3, 6, 12, 24])
def test_horizon_lengths(h):
    """horizon param respected"""
    assert len(c.get(f"/v1/forecast?horizon={h}").json()["forecast"]) == h

@pytest.mark.parametrize("h", [0, 25, -1])
def test_horizon_rejected(h):
    """out of range -> 422"""
    assert c.get(f"/v1/forecast?horizon={h}").status_code == 422

def test_band_nesting():
    """lo_95 <= lo_80 <= forecast <= hi_80 <= hi_95; stress wider than standard"""
    for p in c.get("/v1/forecast").json()["forecast"]:
        assert p["lo_95"] <= p["lo_80"] <= p["forecast"] <= p["hi_80"] <= p["hi_95"]
        assert p["lo_80_stress"] <= p["lo_80"] and p["hi_80_stress"] >= p["hi_80"]

def test_history_matches_csv():
    """/v1/history returns raw prices from price_data.csv"""
    raw = pd.read_csv(ROOT / "price_data.csv"); j = c.get("/v1/history?months=600").json()["points"]
    assert len(j) == 249 and j[-1] == {"month": "2025-09", "price": 15750.0} and [p["price"] for p in j] == raw.avg_monthly_price.tolist()

def test_history_limit():
    """months param limits rows"""
    assert len(c.get("/v1/history?months=24").json()["points"]) == 24

def test_model_info():
    """/v1/model exposes version, CV MAPE, last price"""
    j = c.get("/v1/model").json(); assert j["last_price"] == 15750 and round(j["cv_mape"], 1) == 14.8 and j["last_date"] == "2025-09"

def test_cors_for_react_dev_origin():
    """CORS allows the Vite dev and preview origins"""
    for o in ["http://localhost:5173", "http://localhost:4173"]:
        assert c.get("/health", headers={"Origin": o}).headers["access-control-allow-origin"] == o

def test_cors_blocks_unknown_origin():
    """Unknown origin gets no CORS header"""
    assert "access-control-allow-origin" not in c.get("/health", headers={"Origin": "http://evil.example"}).headers

def test_key_enforced_when_required(monkeypatch):
    """REQUIRE_KEY=1 -> 401 without key, 200 with key (production behind Django)"""
    monkeypatch.setenv("REQUIRE_KEY", "1"); monkeypatch.setenv("SERVICE_KEY", "s3")
    assert c.get("/v1/forecast").status_code == 401 and c.get("/v1/forecast", headers={"x-api-key": "s3"}).status_code == 200
