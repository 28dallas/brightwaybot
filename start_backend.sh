#!/bin/bash

echo "🚀 Starting Deriv Trading Bot Backend..."
echo "======================================"

# Check if .env file exists and has API token
if [ ! -f ".env" ] || ! grep -q "DERIV_API_TOKEN=" .env; then
    echo "❌ Error: .env file not found or missing DERIV_API_TOKEN"
    echo "Please create a .env file with your Deriv API token:"
    echo "DERIV_API_TOKEN=your_actual_token_here"
    exit 1
fi

# Check if API token is set to placeholder
if grep -q "your_deriv_api_token_here" .env; then
    echo "⚠️  Warning: Using placeholder API token"
    echo "Please replace 'your_deriv_api_token_here' with your actual Deriv API token"
    echo "Get your token from: https://app.deriv.com/account/api-token"
    echo ""
fi

# Clear any existing database locks
if [ -f "volatility_data.db" ]; then
    echo "🗃️  Clearing database locks..."
    rm -f volatility_data.db
fi

# Start the backend server
echo "🌐 Starting backend server on http://localhost:8000"
cd backend
python main.py
