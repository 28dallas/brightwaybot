#!/bin/bash

echo "🚀 Starting Volatility 100 AI Trading System"
echo "============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Deriv API token"
fi

# Start backend
echo "🔧 Starting backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend server started successfully (PID: $BACKEND_PID)"
    echo "🌐 Backend running on: http://localhost:8000"
    echo ""
    echo "📊 API Endpoints:"
    echo "   - WebSocket: ws://localhost:8000/ws"
    echo "   - Trading Config: POST /api/trading/config"
    echo "   - Start Trading: POST /api/trading/start"
    echo "   - Stop Trading: POST /api/trading/stop"
    echo "   - AI Status: GET /api/ai/status"
    echo "   - Train AI: POST /api/ai/train"
    echo ""
    echo "🎯 For demo testing, run: python3 demo_trading.py"
    echo "🌐 For frontend, run: cd frontend && npm start"
    echo ""
    echo "Press Ctrl+C to stop the server"
    
    # Keep script running
    wait $BACKEND_PID
else
    echo "❌ Failed to start backend server"
    exit 1
fi