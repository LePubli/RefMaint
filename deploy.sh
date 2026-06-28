#!/bin/bash
set -e

# Start backend with gunicorn
cd /home/runner/workspace/backend
gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind localhost:8000 &

# Serve built frontend with a simple server on port 5000
cd /home/runner/workspace/frontend
npx serve dist -p 5000 -s
