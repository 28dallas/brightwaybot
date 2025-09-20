# Real Trading Setup Guide

## ✅ Your System is Ready for Real Trading!

Your backend code is **already properly configured** to use your Deriv API token for real trading. Here's how it works:

## 🔧 How Real Trading Works

### 1. **API Token Integration**
Your `backend/main.py` already reads the API token from `.env`:
```python
# Line 17: Load environment variables
load_dotenv()

# Line 175: Get token from environment
self.api_token = api_token or os.getenv('DERIV_API_TOKEN')
```

### 2. **Real vs Demo Mode**
- **With API Token**: Connects to real Deriv account, uses real balance
- **Without API Token**: Uses demo mode with $1000 balance

### 3. **Balance Updates**
```python
# Line 446: Real balance if token exists
balance = await deriv_client.refresh_balance_once() if deriv_client.api_token else deriv_client.balance
```

### 4. **Real Trading**
When you click "Start Trading" in the frontend:
- Connects to Deriv's real API
- Places actual trades with real money
- Updates real balance after each trade

## 🚀 Setup Steps

### Step 1: Get Your API Token
1. Go to: https://app.deriv.com/account/api-token
2. Create new token with these scopes:
   - ✅ `payments` (to read balance)
   - ✅ `trading_information` (to place trades)
   - ✅ `read` (to get account info)

### Step 2: Configure Environment
```bash
# Run the setup script
python setup_env.py

# Enter your real API token when prompted
```

### Step 3: Test Connection
```bash
# Test if your token works
python test_deriv_connection.py
```

### Step 4: Start Trading
```bash
# Terminal 1: Backend
./start_backend.sh

# Terminal 2: Frontend
cd frontend && npm start
```

## 📊 What You'll See

### With Real API Token:
- **Balance**: Shows your actual Deriv account balance
- **Trading**: Places real trades with real money
- **P&L**: Real profit/loss updates
- **Status**: "Live" mode in the interface

### Without API Token:
- **Balance**: Shows $1000 (demo)
- **Trading**: Simulated trades only
- **P&L**: Demo profit/loss
- **Status**: "Simulation" mode

## 🔍 Verify Real Trading

1. **Check Logs**: Look for "Connected to Deriv API successfully"
2. **Balance Display**: Should show your real account balance
3. **Trade Results**: Real trades will appear in your Deriv account
4. **API Response**: WebSocket will send real balance updates

## ⚠️ Important Notes

- **Real Money**: With valid API token, trades use real money
- **Risk Management**: Set stop-loss and take-profit limits
- **Token Security**: Keep your API token secure
- **Account Type**: Make sure you're using the right account (demo/real)

## 🎯 Your System Status

✅ **Database**: Fixed concurrency issues
✅ **WebSocket**: Real-time balance updates
✅ **API Integration**: Ready for real trading
✅ **Error Handling**: Comprehensive logging
✅ **Balance Display**: Shows real or demo balance

**Your bot will trade with real money once you add a valid API token!** 🚀

## 🧪 Test Commands

```bash
# Test API connection
python test_deriv_connection.py

# Test balance updates
python test_balance.py

# Demo trading simulation
python demo_balance_fixed.py
```

Ready to trade with real money! 💰📈
