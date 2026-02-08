#!/bin/bash
# Quick start script for ODRA system

set -e

PROJECT_DIR="/Users/danikosnarev/Desktop/ODRA 2"
cd "$PROJECT_DIR"

# Activate venv
source .venv/bin/activate

echo "════════════════════════════════════════════════════════════════"
echo "🚀 STARTING ODRA SYSTEM"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Initialize database if needed
if [ ! -f "odra.db" ]; then
    echo "🔧 Initializing database..."
    python init_db.py
    echo ""
fi

# Start Backend API
echo "📌 Starting Backend API on http://localhost:8000..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo ""

# Wait for backend to start
sleep 3

# Start Frontend
echo "📌 Starting Frontend Dev Server on http://localhost:5173..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ ODRA SYSTEM STARTED!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Access the application:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   Docs:      http://localhost:8000/docs"
echo ""
echo "📊 API Documentation:"
echo "   Swagger UI: http://localhost:8000/docs"
echo "   ReDoc:      http://localhost:8000/redoc"
echo ""
echo "🧪 To run integration tests:"
echo "   python test_integration.py"
echo ""
echo "⏹️  To stop the system, press Ctrl+C"
echo ""

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
