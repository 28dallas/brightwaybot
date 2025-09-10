# Volatility 100 Trading Dashboard

A real-time web application for tracking Volatility 100 Index data, analyzing digit patterns, and automated trading with risk management.

## Features

- **Real-time Data Feed**: Connects to live Volatility 100 (1s) Index data
- **Digit Analysis**: Captures and analyzes last digit frequency (0-9) from prices
- **AI Predictions**: Algorithm suggests most/least likely digits to appear
- **Live Dashboard**: Real-time charts and frequency visualization
- **Auto Trading**: Configurable automated trading with Deriv API integration
- **Risk Management**: Stop-loss and take-profit controls
- **Historical Data**: SQLite database for storing tick and trade history

## Tech Stack

- **Backend**: Python FastAPI with WebSocket support
- **Frontend**: React with TailwindCSS
- **Charts**: Recharts for data visualization
- **Database**: SQLite for data persistence
- **API**: Deriv API for live data and trading

## Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r ../requirements.txt
```

3. Set up environment variables:
```bash
cp ../.env.example .env
# Edit .env with your Deriv API token
```

4. Run the backend server:
```bash
python main.py
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## Configuration

### Deriv API Setup

1. Create a Deriv account at https://deriv.com
2. Generate an API token from your account settings
3. Add the token to your `.env` file:
```
DERIV_API_TOKEN=your_token_here
```

### Trading Configuration

The app allows you to configure:
- **Stake Size**: Amount to risk per trade ($)
- **Duration**: Number of ticks for each trade (1-10)
- **Strategy**: Choose between "Matches" or "Differs"
- **Stop Loss**: Maximum loss threshold ($)
- **Take Profit**: Profit target ($)

## Usage

1. **Start the Application**:
   - Backend runs on `http://localhost:8000`
   - Frontend runs on `http://localhost:3000`

2. **Monitor Live Data**:
   - View real-time price updates
   - Analyze digit frequency patterns
   - Check AI predictions

3. **Configure Trading**:
   - Set your preferred stake size and duration
   - Choose trading strategy (Matches/Differs)
   - Set risk management parameters

4. **Start Auto Trading**:
   - Click "Start Auto Trading" to begin
   - Monitor trades and P&L in real-time
   - Stop trading anytime with the stop button

## API Endpoints

- `GET /api/history` - Retrieve historical tick and trade data
- `POST /api/trading/config` - Update trading configuration
- `POST /api/trading/start` - Start automated trading
- `POST /api/trading/stop` - Stop automated trading
- `WebSocket /ws` - Real-time data stream

## Risk Warning

⚠️ **Trading involves significant financial risk. Only trade with money you can afford to lose. This software is for educational purposes and should not be considered financial advice.**

## License

MIT License - see LICENSE file for details# brightwaybot
