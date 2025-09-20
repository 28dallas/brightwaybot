import numpy as np
from collections import deque
import logging
from datetime import datetime, timedelta

class AdaptivePositionSizer:
    """Advanced position sizing with dynamic adjustments based on market conditions"""

    def __init__(self):
        self.trade_history = deque(maxlen=100)
        self.balance_history = deque(maxlen=50)
        self.volatility_history = deque(maxlen=20)

        # Base configuration
        self.base_position_size = 1.0
        self.max_position_pct = 0.05  # Max 5% of balance
        self.min_position_size = 0.35
        self.max_position_size = 50.0

        # Risk management parameters
        self.max_consecutive_losses = 3
        self.daily_loss_limit_pct = 0.08  # Max 8% daily loss
        self.weekly_loss_limit_pct = 0.15  # Max 15% weekly loss

        # Adaptive parameters
        self.confidence_multiplier = 1.0
        self.volatility_adjustment = 1.0
        self.performance_adjustment = 1.0

    def calculate_optimal_position(self, balance, confidence, volatility, market_regime='normal'):
        """Calculate optimal position size based on multiple factors"""

        # Base position from Kelly Criterion approximation
        kelly_position = self._calculate_kelly_position(balance, confidence)

        # Apply volatility adjustment
        volatility_adjustment = self._calculate_volatility_adjustment(volatility)

        # Apply market regime adjustment
        regime_adjustment = self._calculate_regime_adjustment(market_regime)

        # Apply performance adjustment
        performance_adjustment = self._calculate_performance_adjustment()

        # Apply confidence adjustment
        confidence_adjustment = self._calculate_confidence_adjustment(confidence)

        # Calculate final position
        final_position = (kelly_position *
                         volatility_adjustment *
                         regime_adjustment *
                         performance_adjustment *
                         confidence_adjustment)

        # Apply balance limits
        max_position = min(
            balance * self.max_position_pct,
            self.max_position_size
        )

        final_position = min(final_position, max_position)
        final_position = max(final_position, self.min_position_size)

        return round(final_position, 2)

    def _calculate_kelly_position(self, balance, confidence):
        """Calculate position size using Kelly Criterion approximation"""
        if confidence < 55:
            return 0  # Don't trade below 55% confidence

        # Convert confidence to win probability
        win_prob = min(confidence / 100, 0.85)  # Cap at 85%
        loss_prob = 1 - win_prob

        # Kelly formula approximation for binary outcomes
        # f = (bp - q) / b where b = payout ratio, p = win prob, q = loss prob
        payout_ratio = 0.95  # Typical Deriv payout
        kelly_fraction = (payout_ratio * win_prob - loss_prob) / payout_ratio

        # Conservative Kelly (use half of calculated fraction)
        conservative_kelly = max(0, min(kelly_fraction * 0.5, 0.02))  # Max 2% of balance

        return balance * conservative_kelly

    def _calculate_volatility_adjustment(self, volatility):
        """Adjust position size based on market volatility"""
        if volatility < 0.0005:  # Low volatility
            return 1.2  # Increase position
        elif volatility < 0.001:  # Normal volatility
            return 1.0  # Normal position
        elif volatility < 0.002:  # High volatility
            return 0.7  # Reduce position
        else:  # Very high volatility
            return 0.4  # Significantly reduce position

    def _calculate_regime_adjustment(self, regime):
        """Adjust position size based on market regime"""
        adjustments = {
            'trending': 1.1,    # Slightly increase in trending markets
            'ranging': 1.0,     # Normal in ranging markets
            'volatile': 0.6,    # Reduce in volatile markets
            'normal': 1.0
        }
        return adjustments.get(regime, 1.0)

    def _calculate_performance_adjustment(self):
        """Adjust position size based on recent performance"""
        if len(self.trade_history) < 5:
            return 1.0

        recent_trades = list(self.trade_history)[-10:]
        recent_win_rate = sum(1 for trade in recent_trades if trade.get('profit', 0) > 0) / len(recent_trades)

        if recent_win_rate > 0.7:
            return 1.15  # Increase position after good performance
        elif recent_win_rate < 0.3:
            return 0.7   # Reduce position after poor performance
        else:
            return 1.0

    def _calculate_confidence_adjustment(self, confidence):
        """Adjust position size based on prediction confidence"""
        if confidence >= 85:
            return 1.3   # High confidence = larger position
        elif confidence >= 75:
            return 1.1   # Good confidence = slightly larger position
        elif confidence >= 65:
            return 1.0   # Normal confidence = normal position
        else:
            return 0.8   # Lower confidence = smaller position

    def update_trade_result(self, stake, profit, confidence, strategy):
        """Update trade history and adjust parameters"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'stake': stake,
            'profit': profit,
            'confidence': confidence,
            'strategy': strategy
        })

        # Update performance adjustments
        self._update_performance_adjustments()

    def _update_performance_adjustments(self):
        """Update performance-based adjustments"""
        if len(self.trade_history) < 3:
            return

        # Check for consecutive losses
        recent_trades = list(self.trade_history)[-self.max_consecutive_losses:]
        consecutive_losses = 0

        for trade in reversed(recent_trades):
            if trade['profit'] < 0:
                consecutive_losses += 1
            else:
                break

        # Reduce position size after consecutive losses
        if consecutive_losses >= 2:
            self.performance_adjustment = 0.6
        elif consecutive_losses >= 1:
            self.performance_adjustment = 0.8
        else:
            self.performance_adjustment = 1.0

    def check_daily_loss_limit(self, current_balance, starting_balance):
        """Check if daily loss limit has been exceeded"""
        if starting_balance <= 0:
            return False

        daily_loss_pct = (starting_balance - current_balance) / starting_balance
        return daily_loss_pct > self.daily_loss_limit_pct

    def check_weekly_loss_limit(self, current_balance, weekly_starting_balance):
        """Check if weekly loss limit has been exceeded"""
        if weekly_starting_balance <= 0:
            return False

        weekly_loss_pct = (weekly_starting_balance - current_balance) / weekly_starting_balance
        return weekly_loss_pct > self.weekly_loss_limit_pct

    def get_position_sizing_report(self):
        """Generate position sizing report"""
        if not self.trade_history:
            return "No trade history available"

        recent_trades = list(self.trade_history)[-10:]

        total_stake = sum(trade['stake'] for trade in recent_trades)
        total_profit = sum(trade['profit'] for trade in recent_trades)
        win_rate = sum(1 for trade in recent_trades if trade['profit'] > 0) / len(recent_trades)

        avg_confidence = np.mean([trade['confidence'] for trade in recent_trades])

        report = "📊 ADAPTIVE POSITION SIZING REPORT:\n"
        report += "=" * 50 + "\n"
        report += f"Recent Trades: {len(recent_trades)}\n"
        report += f"Average Stake: ${total_stake/len(recent_trades):.2f}\n"
        report += f"Total P&L: ${total_profit:.2f}\n"
        report += f"Win Rate: {win_rate:.1%}\n"
        report += f"Average Confidence: {avg_confidence:.1f}%\n"
        report += f"Performance Adjustment: {self.performance_adjustment:.2f}\n"
        report += f"Consecutive Losses: {self._count_consecutive_losses()}\n"

        return report

    def _count_consecutive_losses(self):
        """Count current consecutive losses"""
        count = 0
        for trade in reversed(self.trade_history):
            if trade['profit'] < 0:
                count += 1
            else:
                break
        return count

class AdvancedRiskManager:
    """Advanced risk management with multiple protection layers"""

    def __init__(self):
        self.position_sizer = AdaptivePositionSizer()

        # Risk limits
        self.max_daily_loss_pct = 0.08
        self.max_weekly_loss_pct = 0.15
        self.max_monthly_loss_pct = 0.25
        self.max_consecutive_losses = 3

        # Circuit breaker settings
        self.circuit_breaker_threshold = 5  # Stop after 5 consecutive losses
        self.circuit_breaker_timeout = 30  # Minutes to wait before resuming

        # Time-based limits
        self.max_trades_per_hour = 20
        self.max_trades_per_day = 100

        # State tracking
        self.consecutive_losses = 0
        self.circuit_breaker_active = False
        self.circuit_breaker_until = None

    def should_allow_trade(self, balance, confidence, volatility, strategy):
        """Check if trade should be allowed based on risk management rules"""

        # Check circuit breaker
        if self.circuit_breaker_active:
            if datetime.now() < self.circuit_breaker_until:
                return False, "Circuit breaker active"
            else:
                self.circuit_breaker_active = False

        # Check consecutive losses
        if self.consecutive_losses >= self.circuit_breaker_threshold:
            self.circuit_breaker_active = True
            self.circuit_breaker_until = datetime.now() + timedelta(minutes=self.circuit_breaker_timeout)
            return False, f"Circuit breaker triggered after {self.consecutive_losses} losses"

        # Check confidence threshold
        min_confidence = self._get_minimum_confidence(strategy)
        if confidence < min_confidence:
            return False, f"Confidence {confidence:.1f}% below minimum {min_confidence}% for {strategy}"

        # Check volatility limits
        if volatility > 0.003:  # Very high volatility
            return False, f"Volatility {volatility:.6f} too high"

        return True, "Trade allowed"

    def _get_minimum_confidence(self, strategy):
        """Get minimum confidence threshold for strategy"""
        thresholds = {
            'MATCHES': 75,
            'DIFFERS': 70,
            'HYBRID': 65
        }
        return thresholds.get(strategy, 70)

    def update_trade_result(self, profit, strategy):
        """Update risk management state after trade"""
        if profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        # Update position sizer
        self.position_sizer.update_trade_result(0, profit, 0, strategy)  # Will be updated with actual values

    def get_risk_report(self):
        """Generate comprehensive risk report"""
        report = "🛡️ ADVANCED RISK MANAGEMENT REPORT:\n"
        report += "=" * 50 + "\n"
        report += f"Consecutive Losses: {self.consecutive_losses}\n"
        report += f"Circuit Breaker Active: {self.circuit_breaker_active}\n"
        report += f"Max Consecutive Losses Allowed: {self.circuit_breaker_threshold}\n"

        if self.circuit_breaker_active and self.circuit_breaker_until:
            minutes_left = (self.circuit_breaker_until - datetime.now()).seconds // 60
            report += f"Circuit Breaker Timeout: {minutes_left} minutes\n"

        # Add position sizer report
        report += "\n" + self.position_sizer.get_position_sizing_report()

        return report

class MarketIntelligence:
    """Market intelligence and sentiment analysis"""

    def __init__(self):
        self.market_regimes = deque(maxlen=100)
        self.sentiment_scores = deque(maxlen=50)
        self.economic_events = []

    def analyze_market_conditions(self, prices, digits, current_time=None):
        """Comprehensive market analysis"""
        if current_time is None:
            current_time = datetime.now()

        # Detect market regime
        regime = self._detect_market_regime(prices)

        # Calculate sentiment
        sentiment = self._calculate_market_sentiment(digits, prices)

        # Check for economic events
        event_impact = self._check_economic_events(current_time)

        # Generate trading recommendation
        recommendation = self._generate_trading_recommendation(regime, sentiment, event_impact)

        return {
            'regime': regime,
            'sentiment': sentiment,
            'event_impact': event_impact,
            'recommendation': recommendation,
            'confidence_multiplier': self._calculate_confidence_multiplier(regime, sentiment)
        }

    def _detect_market_regime(self, prices):
        """Detect current market regime"""
        if len(prices) < 20:
            return 'normal'

        # Calculate returns
        returns = np.diff(prices) / prices[:-1]

        # Calculate volatility
        volatility = np.std(returns)

        # Calculate trend
        trend = np.polyfit(range(len(prices)), prices, 1)[0]

        # Classify regime
        if volatility > 0.002:
            return 'volatile'
        elif abs(trend) > 0.0002:
            return 'trending'
        else:
            return 'ranging'

    def _calculate_market_sentiment(self, digits, prices):
        """Calculate market sentiment based on patterns"""
        if len(digits) < 20:
            return 'neutral'

        # Analyze digit patterns for sentiment
        recent_digits = digits[-20:]
        unique_digits = len(set(recent_digits))

        # High diversity might indicate random/choppy market
        if unique_digits >= 8:
            return 'bearish'  # Choppy market often precedes down moves

        # Low diversity might indicate trending/strong market
        elif unique_digits <= 3:
            return 'bullish'  # Strong patterns often indicate trending

        else:
            return 'neutral'

    def _check_economic_events(self, current_time):
        """Check for economic events that might impact trading"""
        # This would integrate with economic calendar APIs
        # For now, return neutral impact
        return 'neutral'

    def _generate_trading_recommendation(self, regime, sentiment, event_impact):
        """Generate trading recommendation based on analysis"""
        if event_impact == 'high':
            return 'AVOID_TRADING'  # Avoid trading during high impact events
        elif regime == 'volatile' and sentiment == 'bearish':
            return 'REDUCE_SIZE'    # Reduce position sizes
        elif regime == 'trending' and sentiment == 'bullish':
            return 'INCREASE_SIZE'  # Increase position sizes
        else:
            return 'NORMAL'         # Normal trading

    def _calculate_confidence_multiplier(self, regime, sentiment):
        """Calculate confidence multiplier based on market conditions"""
        multiplier = 1.0

        # Adjust based on regime
        if regime == 'ranging':
            multiplier *= 1.1  # Higher confidence in ranging markets
        elif regime == 'volatile':
            multiplier *= 0.8  # Lower confidence in volatile markets

        # Adjust based on sentiment
        if sentiment == 'bullish':
            multiplier *= 1.05  # Slightly higher confidence in bullish sentiment
        elif sentiment == 'bearish':
            multiplier *= 0.95  # Slightly lower confidence in bearish sentiment

        return multiplier
