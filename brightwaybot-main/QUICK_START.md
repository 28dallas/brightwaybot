# 🚀 Brightway Trading Bot - Quick Start Guide

## 🔧 Setup (One-time)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test your setup:**
   ```bash
   python test_setup.py
   ```

3. **Configure your Deriv API token (optional for demo):**
   - Edit `.env` file
   - Add your real Deriv API token

## 🎯 Running the Bot

### Option 1: Easy Start (Recommended)
```bash
python start_trading.py
```
This will:
- Start the backend server
- Open the frontend dashboard
- Show you all the URLs

### Option 2: Manual Start
1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open Frontend:**
   - Open `simple_frontend.html` in your browser

## 🎮 Using the Dashboard

### Demo Mode (No API token needed)
1. Click **"Run Demo"** button
2. Watch simulated trading with fake ticks
3. See balance and P&L updates

### Live Trading (Requires API token)
1. Add your Deriv API token to `.env` file
2. Click **"Start Trading"** button
3. Bot will connect to live Deriv data
4. Real trades will be placed automatically

### Stop Trading
- Click **"Stop Trading"** to halt all operations

## 📊 Dashboard Features

- **Real-time tick data** from Volatility 100 index
- **AI predictions** with confidence levels
- **Live balance** and P&L tracking
- **Trade history** and win rate
- **Activity log** with detailed information

## 🤖 AI Features

- **Pattern Recognition:** Detects digit sequences and trends
- **Multi-timeframe Analysis:** Analyzes different time windows
- **Volatility Detection:** Identifies optimal trading conditions
- **Smart Stake Sizing:** Uses Kelly Criterion for position sizing
- **Market Session Bias:** Adjusts for different trading sessions

## ⚠️ Important Notes

- **Demo mode** is safe and uses simulated data
- **Live trading** uses real money - start with small amounts
- **Risk management** is built-in with stop-loss and take-profit
- **Always test** in demo mode first

## 🔗 URLs

- **Frontend Dashboard:** `file://path/to/simple_frontend.html`
- **Backend API:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs`

## 🆘 Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running on port 8000
- Check if `python start_trading.py` shows any errors

### "Import errors"
- Run `pip install -r requirements.txt`
- Run `python test_setup.py` to verify setup

### "No trades happening"
- Check if trading is started (green status indicator)
- Verify AI confidence is above threshold
- In demo mode, trades happen every 10th tick

### "API token issues"
- Verify token in `.env` file is correct
- Check Deriv account has trading permissions
- Try demo mode first to test functionality

## 📈 Strategy Settings

The bot uses these default settings (configurable via API):
- **Stake:** $1.00 per trade
- **Strategy:** Digit matches
- **Confidence threshold:** 70%
- **Stop loss:** $10
- **Take profit:** $20
- **AI prediction:** Enabled
- **Auto stake sizing:** Enabled

## 🎯 Success Tips

1. **Start with demo mode** to understand the system
2. **Use small stakes** when going live
3. **Monitor the activity log** for insights
4. **Let the AI run** - it's designed for automated trading
5. **Check win rate** - aim for 60%+ in demo mode

---

**Happy Trading! 🎉**