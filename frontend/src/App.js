import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import TradingPanel from './components/TradingPanel';
import FrequencyChart from './components/FrequencyChart';
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
    confidence_threshold: 60.0
  });

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to WebSocket');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // If real_balance is present in the message, add it to wsData
      if (data.real_balance !== undefined) {
        setWsData(prev => ({ ...prev, balance: data.real_balance }));
      } else if (data.balance !== undefined) {
        setWsData(prev => ({ ...prev, balance: data.balance }));
      } else {
        setWsData(data);
      }
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
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-white">
              Volatility 100 Tracker
            </h1>
            <div className="flex items-center space-x-4">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Dashboard data={wsData} />
            <div className="mt-8">
              <FrequencyChart data={wsData} />
            </div>
          </div>
          
          <div className="lg:col-span-1">
            <TradingPanel
              config={tradingConfig}
              onConfigUpdate={updateTradingConfig}
              onStartTrading={startTrading}
              onStopTrading={stopTrading}
              tradingStatus={wsData?.trading_status}
              balance={wsData?.balance}
              totalProfit={wsData?.total_profit}
              tradesData={{
                today: wsData?.trades_today || 0,
                wins: wsData?.wins || 0,
                losses: wsData?.losses || 0
              }}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

