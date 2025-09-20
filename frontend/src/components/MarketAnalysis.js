import React from 'react';

const MarketAnalysis = ({ data }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleTimeString();
  };

  const getMarketTrend = () => {
    if (!data?.recent_ticks || data.recent_ticks.length < 5) return 'neutral';
    const recent = data.recent_ticks.slice(-5);
    const up = recent.filter((tick, i) => i > 0 && tick.price > recent[i-1].price).length;
    const down = recent.filter((tick, i) => i > 0 && tick.price < recent[i-1].price).length;

    if (up > down) return 'bullish';
    if (down > up) return 'bearish';
    return 'neutral';
  };

  const getVolatilityLevel = () => {
    if (!data?.recent_ticks || data.recent_ticks.length < 10) return 'low';
    const prices = data.recent_ticks.slice(-10).map(tick => tick.price);
    const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
    const variance = prices.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / prices.length;
    const stdDev = Math.sqrt(variance);

    if (stdDev > 0.5) return 'high';
    if (stdDev > 0.2) return 'medium';
    return 'low';
  };

  const trend = getMarketTrend();
  const volatility = getVolatilityLevel();

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <svg className="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Market Analysis
      </h3>

      <div className="space-y-4">
        {/* Market Trend */}
        <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
          <span className="text-slate-300">Market Trend</span>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              trend === 'bullish' ? 'bg-green-400' :
              trend === 'bearish' ? 'bg-red-400' : 'bg-yellow-400'
            }`}></div>
            <span className="text-white font-medium capitalize">{trend}</span>
          </div>
        </div>

        {/* Volatility Level */}
        <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
          <span className="text-slate-300">Volatility</span>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              volatility === 'high' ? 'bg-red-400' :
              volatility === 'medium' ? 'bg-yellow-400' : 'bg-green-400'
            }`}></div>
            <span className="text-white font-medium capitalize">{volatility}</span>
          </div>
        </div>

        {/* Last Update */}
        <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
          <span className="text-slate-300">Last Update</span>
          <span className="text-white font-medium">
            {formatTime(data?.last_tick?.timestamp)}
          </span>
        </div>

        {/* AI Prediction Confidence */}
        {data?.ai_prediction && (
          <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
            <span className="text-slate-300">AI Confidence</span>
            <div className="flex items-center space-x-2">
              <div className="w-16 h-2 bg-slate-600 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-400 to-blue-400 transition-all duration-300"
                  style={{ width: `${data.ai_prediction.final_confidence || 0}%` }}
                ></div>
              </div>
              <span className="text-white font-medium">
                {data.ai_prediction.final_confidence?.toFixed(1) || '0.0'}%
              </span>
            </div>
          </div>
        )}

        {/* Market Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center p-3 bg-slate-700/30 rounded-lg">
            <div className="text-xs text-slate-400">Total Ticks</div>
            <div className="text-lg font-bold text-blue-400">
              {data?.total_ticks || 0}
            </div>
          </div>
          <div className="text-center p-3 bg-slate-700/30 rounded-lg">
            <div className="text-xs text-slate-400">Avg Price</div>
            <div className="text-lg font-bold text-green-400">
              {data?.recent_ticks?.length > 0
                ? (data.recent_ticks.slice(-10).reduce((sum, tick) => sum + tick.price, 0) / Math.min(10, data.recent_ticks.length)).toFixed(3)
                : '0.000'
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysis;
