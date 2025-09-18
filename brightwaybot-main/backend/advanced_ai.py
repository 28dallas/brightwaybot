import numpy as np
from collections import Counter, deque
import math

class UltraAdvancedPredictor:
    def __init__(self):
        self.prediction_history = []
        self.accuracy_tracker = deque(maxlen=100)
        self.profit_tracker = deque(maxlen=50)
        
    def fibonacci_sequence_detection(self, digits):
        """Detect Fibonacci-like patterns in digit sequences"""
        if len(digits) < 10:
            return {}
        
        scores = {i: 0 for i in range(10)}
        
        # Look for mathematical sequences
        for i in range(len(digits) - 3):
            a, b, c = digits[i], digits[i+1], digits[i+2]
            # Fibonacci-like: next = (a + b) % 10
            expected = (a + b) % 10
            if i+3 < len(digits) and digits[i+3] == expected:
                scores[expected] += 5
                
        return scores
    
    def prime_number_bias(self, digits):
        """Detect bias towards prime digits (2,3,5,7)"""
        primes = [2, 3, 5, 7]
        recent = digits[-20:] if len(digits) >= 20 else digits
        
        scores = {i: 0 for i in range(10)}
        
        # Count prime vs non-prime frequency
        prime_count = sum(1 for d in recent if d in primes)
        non_prime_count = len(recent) - prime_count
        
        if prime_count > non_prime_count * 1.2:  # Prime bias detected
            for prime in primes:
                scores[prime] += 3
        elif non_prime_count > prime_count * 1.2:  # Non-prime bias
            for digit in [0, 1, 4, 6, 8, 9]:
                scores[digit] += 3
                
        return scores
    
    def momentum_oscillator(self, prices):
        """Calculate price momentum for timing"""
        if len(prices) < 10:
            return 0
        
        recent = prices[-10:]
        momentum = 0
        
        for i in range(1, len(recent)):
            if recent[i] > recent[i-1]:
                momentum += 1
            else:
                momentum -= 1
                
        return momentum / len(recent)
    
    def digit_clustering_analysis(self, digits):
        """Detect clustering patterns in digits"""
        if len(digits) < 15:
            return {}
        
        scores = {i: 0 for i in range(10)}
        recent = digits[-15:]
        
        # Look for clusters of similar digits
        for digit in range(10):
            positions = [i for i, d in enumerate(recent) if d == digit]
            
            if len(positions) >= 2:
                # Check if digits are clustered together
                gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                avg_gap = np.mean(gaps) if gaps else 15
                
                if avg_gap < 3:  # Clustered
                    scores[digit] += 4
                elif avg_gap > 8:  # Spread out, due for cluster
                    scores[digit] += 2
                    
        return scores
    
    def volatility_breakout_detection(self, prices):
        """Detect volatility breakouts for better timing"""
        if len(prices) < 20:
            return False
        
        recent = prices[-20:]
        volatility = np.std(recent)
        avg_volatility = np.mean([np.std(prices[i:i+10]) for i in range(len(prices)-10)])
        
        # Breakout if current volatility is significantly higher
        return volatility > avg_volatility * 1.5
    
    def ensemble_prediction(self, digits, prices):
        """Combine all advanced methods"""
        if len(digits) < 20:
            return {'predicted_digit': 5, 'confidence': 15.0}
        
        # Get all prediction methods
        fib_scores = self.fibonacci_sequence_detection(digits)
        prime_scores = self.prime_number_bias(digits)
        cluster_scores = self.digit_clustering_analysis(digits)
        
        # Market timing factors
        momentum = self.momentum_oscillator(prices)
        breakout = self.volatility_breakout_detection(prices)
        
        # Combine scores with weights
        final_scores = {}
        for digit in range(10):
            score = 0
            score += fib_scores.get(digit, 0) * 0.3
            score += prime_scores.get(digit, 0) * 0.25
            score += cluster_scores.get(digit, 0) * 0.25
            
            # Momentum boost
            if abs(momentum) > 0.3:
                score += 2
            
            # Breakout boost
            if breakout:
                score += 3
                
            final_scores[digit] = score
        
        # Get best prediction
        best_digit = max(final_scores, key=final_scores.get)
        confidence = min(final_scores[best_digit] * 8 + 20, 95)
        
        return {
            'predicted_digit': best_digit,
            'confidence': confidence,
            'momentum': momentum,
            'breakout': breakout
        }
    
    def adaptive_confidence_adjustment(self, base_confidence):
        """Adjust confidence based on recent performance"""
        if len(self.accuracy_tracker) < 10:
            return base_confidence
        
        recent_accuracy = np.mean(list(self.accuracy_tracker)[-10:])
        
        if recent_accuracy > 0.7:  # Good performance
            return min(base_confidence * 1.15, 95)
        elif recent_accuracy < 0.5:  # Poor performance
            return max(base_confidence * 0.85, 15)
        
        return base_confidence
    
    def kelly_criterion_advanced(self, confidence, balance, recent_wins):
        """Advanced Kelly Criterion with win streak consideration"""
        win_prob = confidence / 100
        payout_ratio = 0.95
        
        # Adjust for recent performance
        if len(recent_wins) >= 5:
            recent_win_rate = np.mean(recent_wins)
            win_prob = (win_prob + recent_win_rate) / 2
        
        # Kelly formula with safety margin
        kelly_fraction = (payout_ratio * win_prob - (1 - win_prob)) / payout_ratio
        kelly_fraction = max(0, min(kelly_fraction * 0.5, 0.1))  # Conservative
        
        optimal_stake = balance * kelly_fraction
        return min(optimal_stake, 5.0)  # Max $5 per trade