import React, { useEffect, useRef } from 'react';

const LiveChart = ({ data }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data?.recent_ticks || data.recent_ticks.length === 0) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    const ticks = data.recent_ticks.slice(-50); // Last 50 ticks
    if (ticks.length < 2) return;

    // Calculate price range
    const prices = ticks.map(tick => tick.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice || 1;

    // Chart settings
    const padding = 20;
    const chartWidth = width - (padding * 2);
    const chartHeight = height - (padding * 2);

    // Draw grid lines
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 0.5;

    // Vertical grid lines
    for (let i = 0; i <= 5; i++) {
      const x = padding + (chartWidth / 5) * i;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, height - padding);
      ctx.stroke();
    }

    // Horizontal grid lines
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Draw price line
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();

    ticks.forEach((tick, index) => {
      const x = padding + (chartWidth / (ticks.length - 1)) * index;
      const y = padding + chartHeight - ((tick.price - minPrice) / priceRange) * chartHeight;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Draw price points
    ctx.fillStyle = '#3b82f6';
    ticks.forEach((tick, index) => {
      const x = padding + (chartWidth / (ticks.length - 1)) * index;
      const y = padding + chartHeight - ((tick.price - minPrice) / priceRange) * chartHeight;

      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw current price indicator
    if (ticks.length > 0) {
      const lastTick = ticks[ticks.length - 1];
      const lastX = padding + chartWidth;
      const lastY = padding + chartHeight - ((lastTick.price - minPrice) / priceRange) * chartHeight;

      // Vertical line
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(lastX, padding);
      ctx.lineTo(lastX, height - padding);
      ctx.stroke();
      ctx.setLineDash([]);

      // Price label
      ctx.fillStyle = '#ef4444';
      ctx.font = '12px monospace';
      ctx.textAlign = 'left';
      ctx.fillText(lastTick.price.toFixed(3), lastX + 5, lastY - 5);

      // Current price dot
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
      ctx.stroke();
    }

  }, [data?.recent_ticks]);

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center">
          <svg className="w-5 h-5 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Live Price Chart
        </h3>

        {data?.last_tick && (
          <div className="text-right">
            <div className="text-sm text-slate-400">Current Price</div>
            <div className="text-lg font-bold text-green-400">
              {data.last_tick.price.toFixed(3)}
            </div>
          </div>
        )}
      </div>

      <div className="relative">
        <canvas
          ref={canvasRef}
          width={600}
          height={300}
          className="w-full h-auto border border-slate-600 rounded bg-slate-900/50"
        />

        {/* Chart overlay info */}
        <div className="absolute top-2 left-2 bg-slate-900/80 backdrop-blur-sm rounded px-2 py-1">
          <div className="text-xs text-slate-300">
            Last {data?.recent_ticks?.length || 0} ticks
          </div>
        </div>

        {/* Price range indicator */}
        {data?.recent_ticks && data.recent_ticks.length > 0 && (
          <div className="absolute bottom-2 right-2 bg-slate-900/80 backdrop-blur-sm rounded px-2 py-1">
            <div className="text-xs text-slate-300">
              Range: {(() => {
                const prices = data.recent_ticks.slice(-50).map(tick => tick.price);
                const min = Math.min(...prices);
                const max = Math.max(...prices);
                return (max - min).toFixed(3);
              })()}
            </div>
          </div>
        )}
      </div>

      {/* Chart legend */}
      <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-0.5 bg-blue-400"></div>
          <span className="text-slate-300">Price Trend</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-0.5 border-t-2 border-dashed border-red-400"></div>
          <span className="text-slate-300">Current Price</span>
        </div>
      </div>
    </div>
  );
};

export default LiveChart;
