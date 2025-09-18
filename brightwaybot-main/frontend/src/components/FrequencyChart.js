import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const FrequencyChart = ({ data }) => {
  const [chartData, setChartData] = useState([]);
  const [viewType, setViewType] = useState('frequency');

  useEffect(() => {
    if (data && data.analysis) {
      const timestamp = new Date(data.timestamp).toLocaleTimeString();
      
      if (viewType === 'frequency') {
        const frequencyData = Object.entries(data.analysis.frequencies || {}).map(([digit, count]) => ({
          digit: parseInt(digit),
          count,
          percentage: data.analysis.percentages[digit] || 0
        }));
        setChartData(frequencyData);
      } else {
        // Time series data
        setChartData(prev => {
          const newData = [...prev, {
            time: timestamp,
            digit: data.last_digit,
            price: data.price
          }].slice(-50); // Keep last 50 points
          return newData;
        });
      }
    }
  }, [data, viewType]);

  const renderFrequencyChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis 
          dataKey="digit" 
          stroke="#9CA3AF"
          tick={{ fill: '#9CA3AF' }}
        />
        <YAxis 
          stroke="#9CA3AF"
          tick={{ fill: '#9CA3AF' }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#1F2937', 
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#F9FAFB'
          }}
        />
        <Bar 
          dataKey="count" 
          fill="#3B82F6"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );

  const renderTimeSeriesChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis 
          dataKey="time" 
          stroke="#9CA3AF"
          tick={{ fill: '#9CA3AF', fontSize: 10 }}
          interval="preserveStartEnd"
        />
        <YAxis 
          domain={[0, 9]}
          stroke="#9CA3AF"
          tick={{ fill: '#9CA3AF' }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#1F2937', 
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#F9FAFB'
          }}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="digit" 
          stroke="#10B981" 
          strokeWidth={2}
          dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
          name="Last Digit"
        />
      </LineChart>
    </ResponsiveContainer>
  );

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Analytics</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setViewType('frequency')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewType === 'frequency' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Frequency
          </button>
          <button
            onClick={() => setViewType('timeseries')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewType === 'timeseries' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Time Series
          </button>
        </div>
      </div>

      <div className="mb-4">
        {viewType === 'frequency' ? (
          <div>
            <h3 className="text-lg font-semibold mb-2">Digit Frequency Distribution</h3>
            <p className="text-sm text-gray-400 mb-4">
              Shows how often each digit (0-9) appears as the last digit of prices
            </p>
            {renderFrequencyChart()}
          </div>
        ) : (
          <div>
            <h3 className="text-lg font-semibold mb-2">Last Digit Over Time</h3>
            <p className="text-sm text-gray-400 mb-4">
              Real-time trend of last digits from recent price ticks
            </p>
            {renderTimeSeriesChart()}
          </div>
        )}
      </div>

      {/* Quick Stats */}
      {data && data.analysis && (
        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {data.analysis.total_ticks}
            </div>
            <div className="text-xs text-gray-400">Total Ticks</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {data.analysis.prediction?.confidence}%
            </div>
            <div className="text-xs text-gray-400">Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">
              {data.last_digit}
            </div>
            <div className="text-xs text-gray-400">Current Digit</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FrequencyChart;