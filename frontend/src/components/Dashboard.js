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

  const { analysis, price, last_digit, timestamp } = data;
  const { frequencies, percentages, most_frequent, least_frequent, prediction } = analysis;

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
        {data?.selected_number !== undefined && (
          <div className="mt-3 p-2 bg-blue-900 rounded">
            <span className="text-sm text-blue-300">Trading Number: </span>
            <span className="font-bold text-blue-100">{data.selected_number}</span>
            <span className="text-sm text-blue-300 ml-2">Strategy: </span>
            <span className="font-bold text-blue-100 capitalize">{data.strategy}</span>
          </div>
        )}
      </div>

      {/* Predictions */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">AI Predictions</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-green-900 rounded-lg p-4">
            <h3 className="font-semibold text-green-400 mb-2">Matches Prediction</h3>
            <div className="text-2xl font-bold text-green-300">
              {prediction?.matches}
            </div>
            <div className="text-sm text-green-400">
              Most likely to repeat
            </div>
          </div>
          <div className="bg-red-900 rounded-lg p-4">
            <h3 className="font-semibold text-red-400 mb-2">Differs Prediction</h3>
            <div className="text-2xl font-bold text-red-300">
              {prediction?.differs}
            </div>
            <div className="text-sm text-red-400">
              Least likely to appear
            </div>
          </div>
        </div>
        <div className="mt-4 text-center">
          <span className="text-sm text-gray-400">
            Confidence: {prediction?.confidence}%
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