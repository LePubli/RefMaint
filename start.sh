#!/bin/bash
set -e

# Start backend in background
cd /home/runner/workspace/backend
python -m uvicorn app.main:app --host localhost --port 8000 --reload &
BACKEND_PID=$!

echo "Backend started (PID: $BACKEND_PID)"

# Start frontend
cd /home/runner/workspace/frontend
npm run dev
