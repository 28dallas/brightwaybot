import React from 'react';

const Dashboard = ({ data }) => {
  if (!data || !data.analysis) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Live Dashboard</h2>
        <p className="text-gray-400">Waiting for data...</p>
      </div>
    );
  }

  const { analysis, price, last_digit, timestamp, ai_prediction } = data;
  const { frequencies, percentages, most_frequent, least_frequent } = analysis;

  return (
    <div className="space-y-6">
      {/* Current Price */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Current Price</h2>
        <div className="flex items-center space-x-4">
          <div className="text-3xl font-mono font-bold text-green-400">
            {price?.toFixed(5)}
          </div>
          <div className="text-lg">
            Last Digit: <span className={`font-bold text-2xl px-2 py-1 rounded ${last_digit === data?.selected_number ? 'bg-yellow-500 text-black' : 'text-yellow-400'}`}>
              {last_digit}
            </span>
          </div>
        </div>
        <div className="text-sm text-gray-400 mt-2">
          {new Date(timestamp).toLocaleTimeString()}
        </div>
        {data?.config?.selected_number !== undefined && (
          <div className="mt-3 p-2 bg-blue-900 rounded">
            <span className="text-sm text-blue-300">Trading Number: </span>
            <span className="font-bold text-blue-100">{data.config.selected_number}</span>
            <span className="text-sm text-blue-300 ml-2">Strategy: </span>
            <span className="font-bold text-blue-100 capitalize">{data.config.strategy}</span>
            <span className={`ml-2 px-2 py-1 rounded text-xs ${last_digit === data.config.selected_number ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'}`}>
              {last_digit === data.config.selected_number ? 'MATCH!' : 'No Match'}
            </span>
          </div>
        )}
      </div>

      {/* AI Predictions */}
      {ai_prediction && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">AI Predictions</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-purple-900 rounded-lg p-4">
              <h3 className="font-semibold text-purple-400 mb-2">AI Prediction</h3>
              <div className="text-3xl font-bold text-purple-300">
                {ai_prediction.predicted_digit}
              </div>
              <div className="text-sm text-purple-400">
                Neural Network
              </div>
            </div>
            <div className="bg-blue-900 rounded-lg p-4">
              <h3 className="font-semibold text-blue-400 mb-2">Confidence</h3>
              <div className="text-2xl font-bold text-blue-300">
                {ai_prediction.final_confidence?.toFixed(1)}%
              </div>
              <div className="text-sm text-blue-400">
                {ai_prediction.final_confidence >= (data?.config?.confidence_threshold || 60) ? 'Above threshold' : 'Below threshold'}
              </div>
            </div>
            <div className="bg-green-900 rounded-lg p-4">
              <h3 className="font-semibold text-green-400 mb-2">Optimal Stake</h3>
              <div className="text-2xl font-bold text-green-300">
                ${ai_prediction.optimal_stake?.toFixed(2) || '0.00'}
              </div>
              <div className="text-sm text-green-400">
                Kelly Criterion
              </div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded p-3">
              <div className="text-sm text-gray-400">Market Session</div>
              <div className="font-bold capitalize">{ai_prediction.market_session}</div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-sm text-gray-400">Volatility Status</div>
              <div className={`font-bold ${ai_prediction.volatility?.trade_favorable ? 'text-green-400' : 'text-red-400'}`}>
                {ai_prediction.volatility?.trade_favorable ? 'Favorable' : 'Unfavorable'}
              </div>
            </div>
          </div>
          <div className="mt-4 text-center">
            <span className={`px-3 py-1 rounded text-sm font-medium ${
              ai_prediction.should_trade ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
            }`}>
              {ai_prediction.should_trade ? 'AI Recommends Trade' : 'AI Says Wait'}
            </span>
          </div>
        </div>
      )}

      {/* Trading Status */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Trading Status</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className={`rounded-lg p-4 ${data?.config?.use_ai_prediction ? 'bg-purple-900' : 'bg-green-900'}`}>
            <h3 className="font-semibold mb-2">
              {data?.config?.use_ai_prediction ? (
                <span className="text-purple-400">AI Mode</span>
              ) : (
                <span className="text-green-400">Manual Mode</span>
              )}
            </h3>
            <div className="text-3xl font-bold">
              {data?.config?.use_ai_prediction ? (
                <span className="text-purple-300">{ai_prediction?.predicted_digit || 'N/A'}</span>
              ) : (
                <span className="text-green-300">{data?.config?.selected_number || 'N/A'}</span>
              )}
            </div>
            <div className="text-sm">
              {data?.config?.use_ai_prediction ? (
                <span className="text-purple-400">Strategy: {data?.config?.strategy}</span>
              ) : (
                <span className="text-green-400">Strategy: {data?.config?.strategy}</span>
              )}
            </div>
          </div>
          <div className="bg-blue-900 rounded-lg p-4">
            <h3 className="font-semibold text-blue-400 mb-2">Current Confidence</h3>
            <div className="text-2xl font-bold text-blue-300">
              {data?.config?.use_ai_prediction ? 
                (ai_prediction?.final_confidence?.toFixed(1) || '0.0') :
                (analysis?.confidence?.toFixed(1) || '0.0')
              }%
            </div>
            <div className="text-sm text-blue-400">
              Threshold: {data?.config?.confidence_threshold || 60}%
            </div>
          </div>
        </div>
        <div className="mt-4 text-center">
          <span className={`px-3 py-1 rounded text-sm font-medium ${
            data?.is_trading ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
          }`}>
            {data?.is_trading ? 
              (data?.config?.use_ai_prediction ? 'AI Trading Active' : 'Manual Trading Active') :
              'Trading Inactive'
            }
          </span>
        </div>
      </div>

      {/* Digit Frequency Grid */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Digit Frequency</h2>
        <div className="grid grid-cols-5 gap-3 mb-4">
          {Object.entries(frequencies || {}).map(([digit, count]) => {
            let className = 'digit-box digit-normal';
            if (digit === most_frequent?.digit) {
              className = 'digit-box digit-most';
            } else if (digit === least_frequent?.digit) {
              className = 'digit-box digit-least';
            }
            
            return (
              <div key={digit} className={className}>
                <div className="text-center">
                  <div className="font-bold">{digit}</div>
                  <div className="text-xs">{count}</div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Percentage bars */}
        <div className="space-y-2">
          {Object.entries(percentages || {}).map(([digit, percentage]) => (
            <div key={digit} className="flex items-center space-x-3">
              <span className="w-4 text-sm font-mono">{digit}</span>
              <div className="flex-1 bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              <span className="w-12 text-xs text-gray-400">
                {percentage.toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Statistics */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Statistics</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-400">Most Frequent</div>
            <div className="text-lg font-bold text-green-400">
              {most_frequent?.digit} ({most_frequent?.count} times)
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Least Frequent</div>
            <div className="text-lg font-bold text-red-400">
              {least_frequent?.digit} ({least_frequent?.count} times)
            </div>
          </div>
        </div>
        <div className="mt-4">
          <div className="text-sm text-gray-400">Total Ticks Analyzed</div>
          <div className="text-lg font-bold">{analysis.total_ticks}</div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;