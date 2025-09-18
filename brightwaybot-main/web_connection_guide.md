# 🌐 Web Interface Connection Guide

## **Option 1: Deriv API Playground (Easiest)**

1. **Go to:** https://api.deriv.com/api-explorer
2. **Connect WebSocket:** `wss://ws.derivws.com/websockets/v3?app_id=1089`
3. **Authorize with your token:** `LrJeQhhpEGKMNGX`
4. **Subscribe to ticks:** `{"ticks": "R_100", "subscribe": 1}`
5. **Use AI predictions from your system to place trades**

## **Option 2: Deriv App Integration**

1. **Login to:** https://app.deriv.com
2. **Switch to Demo Account**
3. **Go to:** Digital Options → Digits
4. **Select:** Volatility 100 (1s) Index
5. **Use your AI system predictions to trade manually**

## **Option 3: Custom Web Dashboard**

Your frontend is ready at: `frontend/src/`

**To start:**
```bash
cd frontend
npm install
npm start
```

**Features:**
- Real-time AI predictions
- Live price feed
- Trading controls
- Performance metrics

## **API Endpoints for Web Integration:**

- **WebSocket:** `ws://localhost:8001/ws`
- **Start Trading:** `POST http://localhost:8001/api/trading/start`
- **Stop Trading:** `POST http://localhost:8001/api/trading/stop`
- **Update Config:** `POST http://localhost:8001/api/trading/config`

## **Trading Flow:**

1. **AI analyzes** live R_100 ticks
2. **Predicts** next digit (0-9)
3. **Calculates** confidence level
4. **Recommends** trade when confidence ≥ 70%
5. **Sizes** position using Kelly Criterion
6. **Places** DIGITMATCH/DIGITDIFF trade

## **Your Settings:**
- **Token:** `LrJeQhhpEGKMNGX`
- **Symbol:** `R_100` (Volatility 100 Index)
- **Contract:** `DIGITMATCH` or `DIGITDIFF`
- **Duration:** 1 tick
- **Confidence Threshold:** 70%