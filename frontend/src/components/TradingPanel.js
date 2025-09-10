import React, { useState } from 'react';

const TradingPanel = ({
  config,
  onConfigUpdate,
  onStartTrading,
  onStopTrading,
  tradingStatus,
  balance,
  totalProfit,
  tradesData
}) => {
  const [localConfig, setLocalConfig] = useState(config);

  const handleConfigChange = (key, value) => {
    const newConfig = { ...localConfig, [key]: value };
    setLocalConfig(newConfig);
    onConfigUpdate(newConfig);
  };

  return (
    <div className="space-y-6">
      {/* Account Info */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Account</h2>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-400">Balance:</span>
            <span className="font-bold text-green-400">
              ${balance?.toFixed(2) || '0.00'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Total P&L:</span>
            <span className={`font-bold ${totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              ${totalProfit?.toFixed(2) || '0.00'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Status:</span>
            <span className={`font-bold ${tradingStatus ? 'text-green-400' : 'text-gray-400'}`}>
              {tradingStatus ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Trades Today:</span>
            <span className="font-bold text-blue-400">
              {tradesData?.today || 0}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Win Rate:</span>
            <span className="font-bold text-green-400">
              {tradesData?.today > 0 ? ((tradesData?.wins || 0) / tradesData.today * 100).toFixed(1) : 0}%
            </span>
          </div>
        </div>
      </div>

      {/* Trading Configuration */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Trading Config</h2>
        
        <div className="space-y-4">
          {/* Selected Number */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Selected Number (0-9)
            </label>
            <select
              value={localConfig.selected_number || 5}
              onChange={(e) => handleConfigChange('selected_number', parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {[0,1,2,3,4,5,6,7,8,9].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          {/* Stake Size */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Stake Size ($)
            </label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={localConfig.stake}
              onChange={(e) => handleConfigChange('stake', parseFloat(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Duration (ticks)
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={localConfig.duration}
              onChange={(e) => handleConfigChange('duration', parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Strategy */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Strategy
            </label>
            <select
              value={localConfig.strategy}
              onChange={(e) => handleConfigChange('strategy', e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="matches">Matches</option>
              <option value="differs">Differs</option>
            </select>
          </div>

          {/* Stop Loss */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Stop Loss ($)
            </label>
            <input
              type="number"
              step="1"
              min="1"
              value={localConfig.stop_loss}
              onChange={(e) => handleConfigChange('stop_loss', parseFloat(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Take Profit */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Take Profit ($)
            </label>
            <input
              type="number"
              step="1"
              min="1"
              value={localConfig.take_profit}
              onChange={(e) => handleConfigChange('take_profit', parseFloat(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Confidence Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Confidence Threshold (%)
            </label>
            <input
              type="number"
              step="5"
              min="0"
              max="100"
              value={localConfig.confidence_threshold || 60}
              onChange={(e) => handleConfigChange('confidence_threshold', parseFloat(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Trading Controls */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Controls</h2>
        
        <div className="space-y-3">
          {!tradingStatus ? (
            <button
              onClick={onStartTrading}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
            >
              Start Auto Trading
            </button>
          ) : (
            <button
              onClick={onStopTrading}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
            >
              Stop Auto Trading
            </button>
          )}
          
          <div className="text-xs text-gray-400 text-center">
            {tradingStatus ? 
              'Auto trading is active. Trades will be placed based on predictions.' :
              'Click to start automated trading based on AI predictions.'
            }
          </div>
        </div>
      </div>

      {/* Risk Warning */}
      <div className="bg-yellow-900 border border-yellow-600 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-400">Risk Warning</h3>
            <div className="mt-1 text-xs text-yellow-300">
              Trading involves significant risk. Only trade with money you can afford to lose.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingPanel;