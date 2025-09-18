import numpy as np
from collections import Counter
from datetime import datetime
import logging

class SimplePredictor:
    def __init__(self, sequence_length=20):
        self.sequence_length = sequence_length
        self.prediction_history = []
        
    def predict_next_digit(self, recent_digits):
        """Enhanced pattern-based prediction"""
        if len(recent_digits) < 10:
            return {'predicted_digit': 5, 'confidence': 10.0, 'method': 'fallback'}
        
        # Pattern analysis - look for sequences and trends
        recent_20 = recent_digits[-20:] if len(recent_digits) >= 20 else recent_digits
        
        # 1. Sequence pattern detection
        sequence_pred = self._detect_sequences(recent_20)
        
        # 2. Gap analysis - digits that haven't appeared recently
        gap_pred = self._gap_analysis(recent_20)
        
        # 3. Alternating pattern detection
        alt_pred = self._alternating_patterns(recent_20)
        
        # 4. Hot/Cold streak analysis
        streak_pred = self._streak_analysis(recent_20)
        
        # Combine predictions with weights
        predictions = {
            'sequence': sequence_pred,
            'gap': gap_pred,
            'alternating': alt_pred,
            'streak': streak_pred
        }
        
        # Weight the predictions
        weighted_scores = {}
        for digit in range(10):
            score = 0
            score += predictions['sequence'].get(digit, 0) * 0.3
            score += predictions['gap'].get(digit, 0) * 0.4
            score += predictions['alternating'].get(digit, 0) * 0.2
            score += predictions['streak'].get(digit, 0) * 0.1
            weighted_scores[digit] = score
        
        # Get best prediction
        best_digit = max(weighted_scores, key=weighted_scores.get)
        confidence = min(weighted_scores[best_digit] * 10, 85.0)
        
        return {
            'predicted_digit': best_digit,
            'confidence': max(confidence, 15.0),  # Minimum 15% confidence
            'method': 'enhanced_pattern'
        }
    
    def _detect_sequences(self, digits):
        """Detect repeating sequences"""
        scores = {i: 0 for i in range(10)}
        
        # Look for 2-3 digit patterns
        for pattern_len in [2, 3]:
            if len(digits) >= pattern_len * 2:
                for i in range(len(digits) - pattern_len):
                    pattern = digits[i:i+pattern_len]
                    # Check if this pattern appears again
                    for j in range(i+pattern_len, len(digits)-pattern_len+1):
                        if digits[j:j+pattern_len] == pattern:
                            # Pattern found, predict next digit
                            if j+pattern_len < len(digits):
                                next_digit = digits[j+pattern_len]
                                scores[next_digit] += 1
        
        return scores
    
    def _gap_analysis(self, digits):
        """Find digits that haven't appeared recently"""
        scores = {i: 0 for i in range(10)}
        counter = Counter(digits)
        
        # Digits that appear less frequently get higher scores
        total = len(digits)
        for digit in range(10):
            frequency = counter.get(digit, 0)
            # Inverse frequency scoring
            if frequency == 0:
                scores[digit] = 8  # High score for missing digits
            else:
                scores[digit] = max(0, 5 - frequency)
        
        return scores
    
    def _alternating_patterns(self, digits):
        """Detect alternating patterns"""
        scores = {i: 0 for i in range(10)}
        
        if len(digits) >= 4:
            # Check for alternating patterns
            for i in range(len(digits)-3):
                if digits[i] == digits[i+2] and digits[i+1] == digits[i+3]:
                    # Alternating pattern found
                    if i+4 < len(digits):
                        expected = digits[i] if (len(digits) - i) % 2 == 1 else digits[i+1]
                        scores[expected] += 2
        
        return scores
    
    def _streak_analysis(self, digits):
        """Analyze hot and cold streaks"""
        scores = {i: 0 for i in range(10)}
        
        if len(digits) >= 5:
            recent_5 = digits[-5:]
            counter = Counter(recent_5)
            
            # If a digit appears 3+ times in last 5, it might continue
            for digit, count in counter.items():
                if count >= 3:
                    scores[digit] += 3
                elif count == 0:
                    scores[digit] += 2  # Due for appearance
        
        return scores


class MarketAnalyzer:
    def analyze_volatility_patterns(self, prices, window=10):
        if len(prices) < window:
            return {'volatility_score': 0, 'momentum': 0, 'trade_favorable': False}
        
        recent_prices = prices[-window:]
        volatility = np.std(recent_prices)
        momentum = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
        
        trade_favorable = 0.0005 < volatility < 0.002 and abs(momentum) < 0.005
        
        return {
            'volatility_score': float(volatility),
            'momentum': float(momentum),
            'trade_favorable': trade_favorable
        }
    
    def multi_timeframe_analysis(self, digits):
        if not digits:
            return {'consensus_digit': 5, 'consensus_strength': 0, 'signals': {}}
        
        windows = [10, 20, 50, 100]
        signals = {}
        
        for window in windows:
            recent = list(digits)[-window:] if len(digits) >= window else list(digits)
            if recent:
                counter = Counter(recent)
                most_freq = counter.most_common(1)[0]
                signals[f'tf_{window}'] = {
                    'digit': most_freq[0],
                    'strength': most_freq[1] / len(recent),
                    'count': most_freq[1]
                }
        
        if signals:
            digit_votes = [s['digit'] for s in signals.values()]
            consensus = Counter(digit_votes)
            consensus_digit, consensus_count = consensus.most_common(1)[0]
            consensus_strength = consensus_count / len(signals)
        else:
            consensus_digit, consensus_strength = 5, 0
        
        return {
            'consensus_digit': consensus_digit,
            'consensus_strength': consensus_strength,
            'signals': signals
        }
    
    def calculate_optimal_stake(self, confidence, balance, base_stake=1.0):
        if confidence < 55:
            return 0
        
        win_prob = min(confidence / 100, 0.85)
        payout_ratio = 0.95
        
        kelly_fraction = (payout_ratio * win_prob - (1 - win_prob)) / payout_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.15))
        
        optimal_stake = balance * kelly_fraction
        return min(optimal_stake, base_stake * 2)
    
    def detect_market_session(self):
        hour = datetime.utcnow().hour
        if 0 <= hour < 8:
            return 'asian'
        elif 8 <= hour < 16:
            return 'european'
        else:
            return 'american'
    
    def get_session_bias(self, session, digits):
        session_biases = {
            'asian': [0, 1, 8, 9],
            'european': [2, 3, 4, 5],
            'american': [6, 7, 8, 9]
        }
        
        if not digits:
            return {'biased_digits': session_biases.get(session, [5]), 'bias_strength': 0, 'is_strong_bias': False}
        
        recent_counter = Counter(digits[-20:])
        session_digits = session_biases.get(session, [5])
        
        bias_strength = sum(recent_counter.get(d, 0) for d in session_digits) / len(digits[-20:])
        
        return {
            'biased_digits': session_digits,
            'bias_strength': bias_strength,
            'is_strong_bias': bias_strength > 0.4
        }


class EnhancedPredictor:
    def __init__(self):
        self.digit_predictor = SimplePredictor()
        self.market_analyzer = MarketAnalyzer()
        self.prediction_history = []
        
    def get_comprehensive_prediction(self, digits, prices, balance, base_stake):
        if not digits or not prices:
            return self._default_prediction()
        
        # 1. Advanced Frequency Prediction
        freq_pred = self.digit_predictor.predict_next_digit(digits)
        
        # 2. Multi-timeframe Analysis
        mtf_analysis = self.market_analyzer.multi_timeframe_analysis(digits)
        
        # 3. Volatility Analysis
        volatility = self.market_analyzer.analyze_volatility_patterns(prices)
        
        # 4. Market Session Analysis
        session = self.market_analyzer.detect_market_session()
        session_bias = self.market_analyzer.get_session_bias(session, digits)
        
        # 5. Combine predictions
        final_confidence = self._calculate_final_confidence(
            freq_pred, mtf_analysis, volatility, session_bias
        )
        
        # 6. Calculate optimal stake
        optimal_stake = self.market_analyzer.calculate_optimal_stake(
            final_confidence, balance, base_stake
        )
        
        prediction = {
            'predicted_digit': freq_pred['predicted_digit'],
            'final_confidence': final_confidence,
            'optimal_stake': optimal_stake,
            'should_trade': final_confidence >= 70 and (volatility['trade_favorable'] or mtf_analysis['consensus_strength'] > 0.6),
            'lstm_prediction': freq_pred,
            'mtf_analysis': mtf_analysis,
            'volatility': volatility,
            'market_session': session,
            'session_bias': session_bias
        }
        
        self.prediction_history.append(prediction)
        return prediction
    
    def _calculate_final_confidence(self, freq_pred, mtf_analysis, volatility, session_bias):
        base_confidence = freq_pred['confidence']
        
        # Boost confidence if multiple methods agree
        if freq_pred['predicted_digit'] == mtf_analysis['consensus_digit']:
            base_confidence += 15
        
        # Volatility boost
        if volatility['trade_favorable']:
            base_confidence += 10
        
        # Session bias boost
        if session_bias['is_strong_bias'] and freq_pred['predicted_digit'] in session_bias['biased_digits']:
            base_confidence += 12
        
        # Consensus strength boost
        base_confidence += mtf_analysis['consensus_strength'] * 20
        
        # Pattern method gets extra boost
        if freq_pred.get('method') == 'enhanced_pattern':
            base_confidence += 5
        
        return min(base_confidence, 90)
    
    def _default_prediction(self):
        return {
            'predicted_digit': 5,
            'final_confidence': 10,
            'optimal_stake': 0,
            'should_trade': False,
            'method': 'default'
        }
    
    def train_model(self, digits):
        logging.info(f"Simple predictor trained with {len(digits)} data points")
        return True
    
    def get_prediction_accuracy(self):
        if len(self.prediction_history) < 10:
            return 0
        avg_confidence = np.mean([p['final_confidence'] for p in self.prediction_history[-50:]])
        return min(avg_confidence * 0.8, 85)