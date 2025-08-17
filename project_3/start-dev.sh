#!/bin/bash
echo "🚀 Starting Employee Engagement Pulse in development mode..."
echo ""
echo "Starting backend on http://localhost:8000"
echo "Starting frontend on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $(jobs -p) 2>/dev/null || true
    wait
    echo "✅ Services stopped"
}

trap cleanup EXIT INT TERM

# Start backend in background
cd backend && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
cd frontend && npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
