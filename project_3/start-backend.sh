#!/bin/bash
echo "🐍 Starting FastAPI backend..."
cd backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
