#!/bin/bash

echo "Starting Volatility 100 Trading Dashboard..."

# Start backend server
echo "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

echo "Application started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

# Wait for user input to stop
read -p "Press Enter to stop the application..."

# Kill both processes
kill $BACKEND_PID $FRONTEND_PID
echo "Application stopped."