# Balance Display Setup Guide

## Problem
Your Deriv balance wasn't showing on the frontend due to database lock errors and missing API configuration.

## ✅ What I Fixed

1. **Database Concurrency Issues**: Added thread-safe database connections with WAL mode
2. **Error Handling**: Improved WebSocket error handling and logging
3. **Balance Updates**: Enhanced balance fetching and real-time updates
4. **Pydantic Compatibility**: Updated deprecated `dict()` to `model_dump()`

## 🚀 How to Get Your Balance Working

### Step 1: Set Up Your Deriv API Token

1. Go to [Deriv Account Settings](https://app.deriv.com/account/api-token)
2. Create a new API token with these scopes:
   - `payments` - to read your balance
   - `trading_information` - to place trades
   - `read` - to get account information

3. Edit your `.env` file and replace the placeholder:
   ```bash
   DERIV_API_TOKEN=your_actual_token_here
   ```

### Step 2: Start the Backend Server

```bash
# Make sure you're in the project root directory
cd /home/nathan/Documents/derivpredict

# Start the backend server
./start_backend.sh
```

### Step 3: Start the Frontend

```bash
# In a new terminal, start the frontend
cd frontend
npm start
```

### Step 4: Test the Balance

```bash
# In another terminal, run the balance test
python test_balance.py
```

## 📊 How Balance Updates Work

1. **Real Balance**: If you have a valid Deriv API token, it fetches your real account balance
2. **Demo Balance**: If no token or demo mode, it uses a default balance of $1000
3. **Live Updates**: Balance updates in real-time when:
   - Trades are placed (profit/loss affects balance)
   - WebSocket sends updates every second
   - Frontend displays the latest balance

## 🔧 Troubleshooting

### Balance Shows $0.00
- Check if your `.env` file has the correct API token
- Verify the token has the right permissions
- Check backend logs for connection errors

### Database Lock Errors
- The fixes I implemented should resolve this
- If you still see errors, try deleting `volatility_data.db` and restarting

### WebSocket Connection Issues
- Make sure backend is running on port 8000
- Check firewall settings
- Verify no other process is using the port

## 📝 Next Steps

1. **Get Real API Token**: Replace the placeholder in `.env`
2. **Test Connection**: Run `python test_balance.py`
3. **Start Trading**: Use the frontend to start/stop trading
4. **Monitor Balance**: Watch the balance update in real-time

## 🎯 Expected Behavior

- **Initial**: Balance shows $1000 (demo) or your real balance
- **During Trading**: Balance updates after each trade
- **P&L Display**: Shows profit/loss in real-time
- **Live Updates**: All stats update every second via WebSocket

The balance should now display correctly and update when you make profits or losses! 🎉
