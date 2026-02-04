#!/bin/bash

echo "🚀 Starting AgentDash..."

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    echo "📦 Using Docker Compose..."
    docker-compose up --build -d
    echo ""
    echo "✅ AgentDash is running!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔌 Backend API: http://localhost:8000"
    echo ""
    echo "To stop: docker-compose down"
    exit 0
fi

# Fallback to manual mode
echo "⚙️ Running in manual mode..."

# Start backend in background
echo "🔧 Starting backend..."
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -q -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ../frontend

echo "🎨 Starting frontend..."
npm install -q
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ AgentDash is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
