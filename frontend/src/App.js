import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import TradingPanel from './components/TradingPanel';
import MarketAnalysis from './components/MarketAnalysis';
import LiveChart from './components/LiveChart';
import './index.css';

function App() {
  const [wsData, setWsData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [tradingConfig, setTradingConfig] = useState({
    stake: 1.0,
    duration: 5,
    strategy: 'matches',
    selected_number: 5,
    stop_loss: 10.0,
    take_profit: 20.0,
    confidence_threshold: 60.0,
    use_ai_prediction: true,
    auto_stake_sizing: true
  });

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to WebSocket');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setWsData(prev => ({ ...prev, ...data }));
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from WebSocket');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  const updateTradingConfig = async (newConfig) => {
    try {
      const response = await fetch('http://localhost:8000/api/trading/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfig),
      });
      
      if (response.ok) {
        setTradingConfig(newConfig);
      }
    } catch (error) {
      console.error('Failed to update trading config:', error);
    }
  };

  const startTrading = async () => {
    try {
      await fetch('http://localhost:8000/api/trading/start', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Failed to start trading:', error);
    }
  };

  const stopTrading = async () => {
    try {
      await fetch('http://localhost:8000/api/trading/stop', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Failed to stop trading:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-700 shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Synthetic AI Trader
                </h1>
                <p className="text-sm text-slate-400">Advanced Volatility 100 Trading System</p>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                <span className="text-sm font-medium">
                  {isConnected ? 'Live' : 'Disconnected'}
                </span>
              </div>

              <div className="hidden md:flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-slate-300">AI Active</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span className="text-slate-300">Real-time</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Live Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Balance</div>
            <div className="text-lg font-bold text-green-400">
              ${wsData?.balance?.toFixed(2) || '0.00'}
            </div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
            <div className="text-xs text-slate-400 uppercase tracking-wide">P&L</div>
            <div className={`text-lg font-bold ${wsData?.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              ${wsData?.pnl?.toFixed(2) || '0.00'}
            </div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Win Rate</div>
            <div className="text-lg font-bold text-blue-400">
              {wsData?.total_trades > 0 ? ((wsData?.wins || 0) / wsData.total_trades * 100).toFixed(1) : 0}%
            </div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Trades</div>
            <div className="text-lg font-bold text-yellow-400">
              {wsData?.total_trades || 0}
            </div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
            <div className="text-xs text-slate-400 uppercase tracking-wide">AI Confidence</div>
            <div className="text-lg font-bold text-purple-400">
              {wsData?.ai_prediction?.final_confidence?.toFixed(1) || '0.0'}%
            </div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Status</div>
            <div className={`text-lg font-bold ${wsData?.is_trading ? 'text-green-400' : 'text-slate-400'}`}>
              {wsData?.is_trading ? 'Trading' : 'Idle'}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Main Dashboard */}
          <div className="xl:col-span-3 space-y-6">
            <Dashboard data={wsData} config={tradingConfig} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LiveChart data={wsData} />
              <MarketAnalysis data={wsData} />
            </div>
          </div>

          {/* Trading Panel */}
          <div className="xl:col-span-1">
            <TradingPanel
              config={tradingConfig}
              onConfigUpdate={updateTradingConfig}
              onStartTrading={startTrading}
              onStopTrading={stopTrading}
              tradingStatus={wsData?.is_trading}
              balance={wsData?.balance}
              totalProfit={wsData?.pnl}
              tradesData={{
                today: wsData?.total_trades || 0,
                wins: wsData?.wins || 0,
                losses: wsData?.losses || 0,
                ai_trained: true,
                ai_accuracy: wsData?.ai_prediction?.final_confidence || 0
              }}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

