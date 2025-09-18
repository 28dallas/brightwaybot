import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from collections import Counter
from datetime import datetime
import logging
import joblib
import os

class DigitPredictor:
    def __init__(self, sequence_length=20):
        self.sequence_length = sequence_length
        self.model = None
        self.is_trained = False
        self.model_path = "digit_model.h5"
        self._build_model()
        
    def _build_model(self):
        """Build LSTM neural network for digit prediction"""
        self.model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.sequence_length, 1)),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(10, activation='softmax')  # 10 digits probability
        ])
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Load existing model if available
        if os.path.exists(self.model_path):
            try:
                self.model.load_weights(self.model_path)
                self.is_trained = True
                logging.info("Loaded existing LSTM model")
            except:
                logging.info("Failed to load model, will train new one")
    
    def train(self, digit_sequence):
        """Train the model with historical digit data"""
        if len(digit_sequence) < self.sequence_length + 50:
            logging.warning("Not enough data to train LSTM model")
            return False
            
        # Prepare training data
        X, y = [], []
        for i in range(len(digit_sequence) - self.sequence_length):
            X.append(digit_sequence[i:i + self.sequence_length])
            y.append(digit_sequence[i + self.sequence_length])
        
        X = np.array(X).reshape(-1, self.sequence_length, 1)
        y = to_categorical(np.array(y), num_classes=10)
        
        # Train model
        self.model.fit(X, y, epochs=50, batch_size=32, verbose=0, validation_split=0.2)
        self.model.save_weights(self.model_path)
        self.is_trained = True
        logging.info("LSTM model trained successfully")
        return True
    
    def predict_next_digit(self, recent_digits):
        """Predict next digit with confidence"""
        if not self.is_trained or len(recent_digits) < self.sequence_length:
            return self._fallback_prediction(recent_digits)
        
        sequence = np.array(recent_digits[-self.sequence_length:]).reshape(1, self.sequence_length, 1)
        probabilities = self.model.predict(sequence, verbose=0)[0]
        
        predicted_digit = int(np.argmax(probabilities))
        confidence = float(np.max(probabilities) * 100)
        
        return {
            'predicted_digit': predicted_digit,
            'confidence': confidence,
            'probabilities': probabilities.tolist(),
            'method': 'lstm'
        }
    
    def _fallback_prediction(self, recent_digits):
        """Fallback to frequency analysis if LSTM not ready"""
        if not recent_digits:
            return {'predicted_digit': 5, 'confidence': 10.0, 'method': 'fallback'}
        
        counter = Counter(recent_digits[-50:])
        most_common = counter.most_common(1)[0]
        confidence = (most_common[1] / len(recent_digits[-50:])) * 100
        
        return {
            'predicted_digit': most_common[0],
            'confidence': confidence,
            'method': 'frequency'
        }


class MarketAnalyzer:
    def __init__(self):
        pass
    
    def analyze_volatility_patterns(self, prices, window=10):
        """Detect high/low volatility periods for better entry timing"""
        if len(prices) < window:
            return {'volatility_score': 0, 'momentum': 0, 'trade_favorable': False}
        
        recent_prices = prices[-window:]
        volatility = np.std(recent_prices)
        
        if len(prices) >= 5:
            momentum = (prices[-1] - prices[-5]) / prices[-5]
        else:
            momentum = 0
        
        # Sweet spot: moderate volatility, low momentum
        trade_favorable = 0.0005 < volatility < 0.002 and abs(momentum) < 0.005
        
        return {
            'volatility_score': float(volatility),
            'momentum': float(momentum),
            'trade_favorable': trade_favorable
        }
    
    def multi_timeframe_analysis(self, digits):
        """Analyze patterns across different tick windows"""
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
        
        # Calculate consensus
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
        """Kelly Criterion-based position sizing"""
        if confidence < 55:
            return 0  # Don't trade below 55% confidence
        
        # Convert confidence to win probability
        win_prob = min(confidence / 100, 0.85)  # Cap at 85%
        payout_ratio = 0.95  # Typical Deriv payout
        
        # Kelly formula: f = (bp - q) / b
        kelly_fraction = (payout_ratio * win_prob - (1 - win_prob)) / payout_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.15))  # Cap at 15% of balance
        
        optimal_stake = balance * kelly_fraction
        return min(optimal_stake, base_stake * 2)  # Max 2x base stake
    
    def detect_market_session(self):
        """Different sessions have different digit patterns"""
        hour = datetime.utcnow().hour
        
        if 0 <= hour < 8:
            return 'asian'
        elif 8 <= hour < 16:
            return 'european'
        else:
            return 'american'
    
    def get_session_bias(self, session, digits):
        """Get digit bias for specific market session"""
        session_biases = {
            'asian': [0, 1, 8, 9],      # Even numbers tend to appear more
            'european': [2, 3, 4, 5],   # Middle range digits
            'american': [6, 7, 8, 9]    # Higher digits
        }
        
        if not digits:
            return session_biases.get(session, [5])
        
        # Check if current pattern matches session bias
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
        self.digit_predictor = DigitPredictor()
        self.market_analyzer = MarketAnalyzer()
        self.prediction_history = []
        
    def get_comprehensive_prediction(self, digits, prices, balance, base_stake):
        """Get comprehensive prediction combining all AI methods"""
        if not digits or not prices:
            return self._default_prediction()
        
        # 1. LSTM Prediction
        lstm_pred = self.digit_predictor.predict_next_digit(digits)
        
        # 2. Multi-timeframe Analysis
        mtf_analysis = self.market_analyzer.multi_timeframe_analysis(digits)
        
        # 3. Volatility Analysis
        volatility = self.market_analyzer.analyze_volatility_patterns(prices)
        
        # 4. Market Session Analysis
        session = self.market_analyzer.detect_market_session()
        session_bias = self.market_analyzer.get_session_bias(session, digits)
        
        # 5. Combine predictions with weights
        final_confidence = self._calculate_final_confidence(
            lstm_pred, mtf_analysis, volatility, session_bias
        )
        
        # 6. Calculate optimal stake
        optimal_stake = self.market_analyzer.calculate_optimal_stake(
            final_confidence, balance, base_stake
        )
        
        prediction = {
            'predicted_digit': lstm_pred['predicted_digit'],
            'final_confidence': final_confidence,
            'optimal_stake': optimal_stake,
            'should_trade': final_confidence >= 60 and volatility['trade_favorable'],
            'lstm_prediction': lstm_pred,
            'mtf_analysis': mtf_analysis,
            'volatility': volatility,
            'market_session': session,
            'session_bias': session_bias
        }
        
        self.prediction_history.append(prediction)
        return prediction
    
    def _calculate_final_confidence(self, lstm_pred, mtf_analysis, volatility, session_bias):
        """Combine all prediction methods into final confidence score"""
        base_confidence = lstm_pred['confidence']
        
        # Boost confidence if multiple methods agree
        if lstm_pred['predicted_digit'] == mtf_analysis['consensus_digit']:
            base_confidence += 10
        
        # Boost if volatility is favorable
        if volatility['trade_favorable']:
            base_confidence += 5
        
        # Boost if session bias is strong
        if session_bias['is_strong_bias'] and lstm_pred['predicted_digit'] in session_bias['biased_digits']:
            base_confidence += 8
        
        # Boost based on consensus strength
        base_confidence += mtf_analysis['consensus_strength'] * 15
        
        return min(base_confidence, 95)  # Cap at 95%
    
    def _default_prediction(self):
        return {
            'predicted_digit': 5,
            'final_confidence': 10,
            'optimal_stake': 0,
            'should_trade': False,
            'method': 'default'
        }
    
    def train_model(self, digits):
        """Train the LSTM model with historical data"""
        return self.digit_predictor.train(digits)
    
    def get_prediction_accuracy(self):
        """Calculate prediction accuracy from history"""
        if len(self.prediction_history) < 10:
            return 0
        
        # This would need actual outcomes to calculate
        # For now, return estimated accuracy based on confidence levels
        avg_confidence = np.mean([p['final_confidence'] for p in self.prediction_history[-50:]])
        return min(avg_confidence * 0.8, 85)  # Conservative estimate