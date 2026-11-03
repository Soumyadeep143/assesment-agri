#!/usr/bin/env bash
# Starts the backend (FastAPI/uvicorn) and frontend (Vite) together.
# Usage: ./run.sh   (Git Bash on Windows, or any POSIX shell)
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PY="$ROOT/venv/Scripts/python.exe"
if [ ! -f "$PY" ]; then
  echo "venv not found at $ROOT/venv — create it first: python -m venv venv && ./venv/Scripts/python.exe -m pip install -r requirements.txt"
  exit 1
fi

if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "Installing frontend dependencies..."
  (cd "$ROOT/frontend" && npm install)
fi

if [ ! -f "$ROOT/frontend/.env" ]; then
  cp "$ROOT/frontend/.env.example" "$ROOT/frontend/.env"
fi

mkdir -p "$ROOT/.logs"

echo "Starting backend (FastAPI) on :8000 ..."
"$PY" -m uvicorn backend.main:app --reload --port 8000 > "$ROOT/.logs/backend.log" 2>&1 &
BACKEND_PID=$!

echo "Starting frontend (Vite) on :5173 ..."
(cd "$ROOT/frontend" && npm run dev) > "$ROOT/.logs/frontend.log" 2>&1 &
FRONTEND_PID=$!

cleanup() {
  echo ""
  echo "Stopping backend (pid $BACKEND_PID) and frontend (pid $FRONTEND_PID)..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo "Backend:  http://localhost:8000  (logs: .logs/backend.log)"
echo "Frontend: http://localhost:5173  (logs: .logs/frontend.log)"
echo "Press Ctrl+C to stop both."
echo ""

wait "$BACKEND_PID" "$FRONTEND_PID"
