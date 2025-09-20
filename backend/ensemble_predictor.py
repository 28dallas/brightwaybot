import numpy as np
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging
from .transformer_predictor import TransformerPredictor, EnsemblePredictor, AdaptivePredictor
from .ai_predictor import EnhancedPredictor

class AdvancedEnsemblePredictor:
    """Advanced ensemble predictor combining multiple AI models with meta-learning"""

    def __init__(self):
        # Initialize all prediction models
        self.transformer_predictor = TransformerPredictor()
        self.lstm_predictor = EnhancedPredictor()
        self.adaptive_predictor = AdaptivePredictor()

        # Model performance tracking
        self.model_performance = defaultdict(lambda: {
            'correct': 0,
            'total': 0,
            'accuracy': 0.0,
            'confidence_sum': 0.0,
            'avg_confidence': 0.0
        })

        # Meta-learner weights (will be updated based on performance)
        self.model_weights = {
            'transformer': 0.3,
            'lstm': 0.3,
            'adaptive': 0.3,
            'frequency': 0.1
        }

        # Prediction history for meta-learning
        self.prediction_history = []
        self.max_history = 1000

    def get_comprehensive_prediction(self, digits, prices, balance, base_stake):
        """Get prediction from advanced ensemble with meta-learning"""
        if not digits or not prices:
            return self._default_prediction()

        # Get predictions from all models
        predictions = self._get_all_predictions(digits, prices, balance, base_stake)

        # Calculate ensemble prediction
        ensemble_pred = self._calculate_ensemble_prediction(predictions)

        # Apply meta-learning adjustments
        final_prediction = self._apply_meta_learning(ensemble_pred, digits, prices)

        # Update model performance tracking
        self._update_model_performance(predictions)

        # Store prediction for future meta-learning
        self.prediction_history.append({
            'timestamp': datetime.now(),
            'prediction': final_prediction,
            'individual_predictions': predictions,
            'market_conditions': self._extract_market_conditions(digits, prices)
        })

        # Keep history size manageable
        if len(self.prediction_history) > self.max_history:
            self.prediction_history = self.prediction_history[-self.max_history:]

        return final_prediction

    def _get_all_predictions(self, digits, prices, balance, base_stake):
        """Get predictions from all available models"""
        predictions = {}

        try:
            # Transformer prediction
            transformer_pred = self.transformer_predictor.predict_next_digit(digits)
            predictions['transformer'] = transformer_pred
        except Exception as e:
            logging.warning(f"Transformer prediction failed: {e}")
            predictions['transformer'] = self._default_prediction()

        try:
            # LSTM prediction (using existing AI predictor)
            lstm_pred = self.lstm_predictor.get_comprehensive_prediction(digits, prices, balance, base_stake)
            predictions['lstm'] = {
                'predicted_digit': lstm_pred['predicted_digit'],
                'confidence': lstm_pred['final_confidence'],
                'method': 'lstm'
            }
        except Exception as e:
            logging.warning(f"LSTM prediction failed: {e}")
            predictions['lstm'] = self._default_prediction()

        try:
            # Adaptive prediction
            adaptive_pred = self.adaptive_predictor.get_adaptive_prediction(digits, prices, balance, base_stake)
            predictions['adaptive'] = {
                'predicted_digit': adaptive_pred['predicted_digit'],
                'confidence': adaptive_pred['confidence'],
                'method': 'adaptive'
            }
        except Exception as e:
            logging.warning(f"Adaptive prediction failed: {e}")
            predictions['adaptive'] = self._default_prediction()

        # Frequency-based prediction
        predictions['frequency'] = self._get_frequency_prediction(digits)

        return predictions

    def _calculate_ensemble_prediction(self, predictions):
        """Calculate weighted ensemble prediction"""
        if not predictions:
            return self._default_prediction()

        # Calculate weighted vote
        digit_votes = defaultdict(float)
        total_weight = 0

        for model_name, pred in predictions.items():
            if pred and 'predicted_digit' in pred and 'confidence' in pred:
                weight = self.model_weights.get(model_name, 0.1)
                confidence = pred['confidence'] / 100.0  # Normalize to 0-1

                # Combine model weight with prediction confidence
                vote_weight = weight * confidence
                digit_votes[pred['predicted_digit']] += vote_weight
                total_weight += vote_weight

        if total_weight == 0:
            return self._default_prediction()

        # Find digit with highest weighted vote
        best_digit = max(digit_votes.items(), key=lambda x: x[1])[0]
        best_weight = digit_votes[best_digit]

        # Calculate ensemble confidence
        ensemble_confidence = (best_weight / total_weight) * 100

        # Get confidence distribution for probabilities
        probabilities = [0] * 10
        for digit, weight in digit_votes.items():
            probabilities[digit] = weight / total_weight

        return {
            'predicted_digit': int(best_digit),
            'confidence': float(ensemble_confidence),
            'probabilities': probabilities,
            'method': 'advanced_ensemble',
            'individual_predictions': predictions,
            'model_weights': self.model_weights.copy()
        }

    def _apply_meta_learning(self, ensemble_pred, digits, prices):
        """Apply meta-learning adjustments based on historical performance"""
        # Market regime adjustment
        regime = self.adaptive_predictor.detect_market_regime(prices)
        regime_adjustment = self._get_regime_adjustment(regime)

        # Pattern-based adjustment
        pattern_adjustment = self._get_pattern_adjustment(digits)

        # Historical performance adjustment
        performance_adjustment = self._get_performance_adjustment()

        # Apply adjustments
        total_adjustment = regime_adjustment + pattern_adjustment + performance_adjustment
        ensemble_pred['confidence'] = min(max(ensemble_pred['confidence'] + total_adjustment, 0), 95)

        # Add adjustment information
        ensemble_pred['meta_adjustments'] = {
            'regime': regime_adjustment,
            'pattern': pattern_adjustment,
            'performance': performance_adjustment,
            'total': total_adjustment
        }

        return ensemble_pred

    def _get_regime_adjustment(self, regime):
        """Get confidence adjustment based on market regime"""
        adjustments = {
            'trending': 5,    # Boost confidence in trending markets
            'ranging': 8,     # Higher confidence in ranging markets
            'volatile': -10   # Reduce confidence in volatile markets
        }
        return adjustments.get(regime, 0)

    def _get_pattern_adjustment(self, digits):
        """Get adjustment based on pattern strength"""
        if len(digits) < 15:
            return 0

        recent = digits[-15:]
        counter = Counter(recent)
        most_common = counter.most_common(1)[0]

        # Strong pattern = higher confidence
        frequency = most_common[1] / len(recent)
        if frequency > 0.6:
            return 8
        elif frequency > 0.4:
            return 4
        elif frequency < 0.2:
            return -5
        else:
            return 0

    def _get_performance_adjustment(self):
        """Get adjustment based on recent model performance"""
        if len(self.prediction_history) < 10:
            return 0

        recent_predictions = self.prediction_history[-20:]
        recent_accuracy = sum(1 for p in recent_predictions if p.get('correct', False)) / len(recent_predictions)

        if recent_accuracy > 0.7:
            return 5
        elif recent_accuracy < 0.4:
            return -8
        else:
            return 0

    def _get_frequency_prediction(self, digits):
        """Get frequency-based prediction"""
        if not digits:
            return {'predicted_digit': 5, 'confidence': 10.0, 'method': 'frequency'}

        counter = Counter(digits[-50:])
        most_common = counter.most_common(1)[0]
        confidence = (most_common[1] / len(digits[-50:])) * 100

        return {
            'predicted_digit': most_common[0],
            'confidence': confidence,
            'method': 'frequency'
        }

    def _update_model_performance(self, predictions):
        """Update model performance tracking"""
        # This would be called when actual outcomes are known
        # For now, just track prediction statistics
        for model_name, pred in predictions.items():
            if pred and 'confidence' in pred:
                self.model_performance[model_name]['total'] += 1
                self.model_performance[model_name]['confidence_sum'] += pred['confidence']
                self.model_performance[model_name]['avg_confidence'] = (
                    self.model_performance[model_name]['confidence_sum'] /
                    self.model_performance[model_name]['total']
                )

    def update_actual_outcome(self, predicted_digit, actual_digit):
        """Update model performance with actual outcome"""
        # Mark the last prediction as correct/incorrect
        if self.prediction_history:
            last_prediction = self.prediction_history[-1]
            last_prediction['actual_digit'] = actual_digit
            last_prediction['correct'] = (last_prediction['prediction']['predicted_digit'] == actual_digit)

            # Update individual model performance
            individual_preds = last_prediction.get('individual_predictions', {})
            for model_name, pred in individual_preds.items():
                if pred and 'predicted_digit' in pred:
                    self.model_performance[model_name]['total'] += 1
                    if pred['predicted_digit'] == actual_digit:
                        self.model_performance[model_name]['correct'] += 1

                    # Update accuracy
                    self.model_performance[model_name]['accuracy'] = (
                        self.model_performance[model_name]['correct'] /
                        self.model_performance[model_name]['total'] * 100
                    )

            # Update model weights based on performance
            self._update_model_weights()

    def _update_model_weights(self):
        """Update model weights based on performance"""
        total_accuracy = sum(
            self.model_performance[model]['accuracy']
            for model in ['transformer', 'lstm', 'adaptive', 'frequency']
            if self.model_performance[model]['total'] > 0
        )

        if total_accuracy > 0:
            for model in ['transformer', 'lstm', 'adaptive', 'frequency']:
                if self.model_performance[model]['total'] > 0:
                    accuracy = self.model_performance[model]['accuracy']
                    self.model_weights[model] = accuracy / total_accuracy

        # Normalize weights to sum to 1
        weight_sum = sum(self.model_weights.values())
        if weight_sum > 0:
            for model in self.model_weights:
                self.model_weights[model] /= weight_sum

    def _extract_market_conditions(self, digits, prices):
        """Extract current market conditions for analysis"""
        return {
            'digit_volatility': self._calculate_digit_volatility(digits),
            'price_volatility': np.std(prices) if len(prices) > 1 else 0,
            'trend_strength': self._calculate_trend_strength(prices),
            'pattern_strength': self._calculate_pattern_strength(digits)
        }

    def _calculate_digit_volatility(self, digits):
        """Calculate volatility in digit sequence"""
        if len(digits) < 5:
            return 0
        return np.std([d for d in digits[-10:]])

    def _calculate_trend_strength(self, prices):
        """Calculate strength of price trend"""
        if len(prices) < 10:
            return 0
        # Simple linear regression slope
        x = np.arange(len(prices))
        slope, _ = np.polyfit(x, prices, 1)
        return abs(slope)

    def _calculate_pattern_strength(self, digits):
        """Calculate strength of repeating patterns"""
        if len(digits) < 10:
            return 0

        # Look for repeating patterns
        recent = digits[-10:]
        counter = Counter(recent)
        most_common = counter.most_common(1)[0]

        return most_common[1] / len(recent)

    def _default_prediction(self):
        return {
            'predicted_digit': 5,
            'confidence': 10,
            'method': 'default'
        }

    def train_models(self, digits):
        """Train all models in the ensemble"""
        success = True

        try:
            success &= self.transformer_predictor.train(digits)
        except Exception as e:
            logging.warning(f"Transformer training failed: {e}")
            success = False

        try:
            success &= self.lstm_predictor.train_model(digits)
        except Exception as e:
            logging.warning(f"LSTM training failed: {e}")
            success = False

        try:
            success &= self.adaptive_predictor.train_models(digits)
        except Exception as e:
            logging.warning(f"Adaptive training failed: {e}")
            success = False

        return success

    def get_model_performance_report(self):
        """Get performance report for all models"""
        report = "🤖 ADVANCED ENSEMBLE MODEL PERFORMANCE:\n"
        report += "=" * 50 + "\n"

        for model_name, stats in self.model_performance.items():
            if stats['total'] > 0:
                accuracy = stats['accuracy']
                avg_confidence = stats['avg_confidence']
                weight = self.model_weights.get(model_name, 0)

                report += f"{model_name.upper()}: {accuracy:.1f}% accuracy, "
                report += f"{avg_confidence:.1f}% avg confidence, "
                report += f"{weight:.2f} weight\n"

        return report
