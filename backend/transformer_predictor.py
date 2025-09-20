import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, Add, Embedding
from tensorflow.keras.utils import to_categorical
from collections import Counter
from datetime import datetime
import logging
import os

class PositionalEncoding(tf.keras.layers.Layer):
    """Positional encoding for transformer models"""

    def __init__(self, sequence_length, d_model):
        super().__init__()
        self.sequence_length = sequence_length
        self.d_model = d_model

    def call(self, inputs):
        # Create position indices
        positions = tf.range(self.sequence_length, dtype=tf.float32)
        positions = tf.expand_dims(positions, 0)  # Add batch dimension

        # Calculate positional encodings
        div_term = tf.exp(tf.range(0, self.d_model, 2, dtype=tf.float32) * (-np.log(10000.0) / self.d_model))

        # Apply sin to even indices, cos to odd indices
        sin_values = tf.sin(positions * div_term)
        cos_values = tf.cos(positions * div_term)

        # Interleave sin and cos values
        pos_encoding = tf.zeros((1, self.sequence_length, self.d_model))
        pos_encoding = tf.tensor_scatter_nd_update(
            pos_encoding,
            [[0, i, j] for i in range(self.sequence_length) for j in range(self.d_model)],
            tf.reshape(tf.concat([sin_values, cos_values], axis=-1), [-1])
        )

        return inputs + pos_encoding

class TransformerBlock(tf.keras.layers.Layer):
    """Transformer encoder block"""

    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.dff = dff
        self.dropout_rate = dropout_rate

        self.attention = MultiHeadAttention(num_heads=num_heads, key_dim=d_model, dropout=dropout_rate)
        self.norm1 = LayerNormalization(epsilon=1e-6)
        self.norm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(dropout_rate)
        self.dropout2 = Dropout(dropout_rate)

        # Feed-forward network
        self.dense1 = Dense(dff, activation='relu')
        self.dense2 = Dense(d_model)

    def call(self, inputs, training=False):
        # Multi-head attention
        attn_output = self.attention(inputs, inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.norm1(inputs + attn_output)

        # Feed-forward network
        ffn_output = self.dense1(out1)
        ffn_output = self.dense2(ffn_output)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.norm2(out1 + ffn_output)

        return out2

class TransformerPredictor:
    def __init__(self, sequence_length=20, d_model=64, num_heads=4, num_layers=2):
        self.sequence_length = sequence_length
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.model = None
        self.is_trained = False
        self.model_path = "transformer_model.h5"
        self._build_model()

    def _build_model(self):
        """Build transformer-based prediction model"""
        inputs = Input(shape=(self.sequence_length,))

        # Embedding layer for digits (0-9)
        embedding = Embedding(10, self.d_model)(inputs)

        # Add positional encoding
        positional_encoding = PositionalEncoding(self.sequence_length, self.d_model)
        x = positional_encoding(embedding)

        # Transformer blocks
        for _ in range(self.num_layers):
            x = TransformerBlock(self.d_model, self.num_heads, self.d_model * 4)(x)

        # Global average pooling
        x = tf.keras.layers.GlobalAveragePooling1D()(x)

        # Output layer
        outputs = Dense(10, activation='softmax')(x)

        self.model = Model(inputs=inputs, outputs=outputs)

        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        # Load existing model if available
        if os.path.exists(self.model_path):
            try:
                self.model.load_weights(self.model_path)
                self.is_trained = True
                logging.info("Loaded existing transformer model")
            except Exception as e:
                logging.info(f"Failed to load transformer model: {e}")

    def train(self, digit_sequence, epochs=30, batch_size=32):
        """Train the transformer model"""
        if len(digit_sequence) < self.sequence_length + 50:
            logging.warning("Not enough data to train transformer model")
            return False

        # Prepare training data
        X, y = [], []
        for i in range(len(digit_sequence) - self.sequence_length):
            X.append(digit_sequence[i:i + self.sequence_length])
            y.append(digit_sequence[i + self.sequence_length])

        X = np.array(X)
        y = to_categorical(np.array(y), num_classes=10)

        # Train model
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )

        self.model.save_weights(self.model_path)
        self.is_trained = True
        logging.info("Transformer model trained successfully")
        return True

    def predict_next_digit(self, recent_digits):
        """Predict next digit using transformer model"""
        if not self.is_trained or len(recent_digits) < self.sequence_length:
            return self._fallback_prediction(recent_digits)

        sequence = np.array(recent_digits[-self.sequence_length:]).reshape(1, -1)
        probabilities = self.model.predict(sequence, verbose=0)[0]

        predicted_digit = int(np.argmax(probabilities))
        confidence = float(np.max(probabilities) * 100)

        return {
            'predicted_digit': predicted_digit,
            'confidence': confidence,
            'probabilities': probabilities.tolist(),
            'method': 'transformer'
        }

    def _fallback_prediction(self, recent_digits):
        """Fallback to frequency analysis"""
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

class EnsemblePredictor:
    """Combines multiple AI models for better predictions"""

    def __init__(self):
        self.transformer_predictor = TransformerPredictor()
        self.prediction_history = []
        self.model_weights = {
            'transformer': 0.4,
            'lstm': 0.4,
            'frequency': 0.2
        }

    def get_ensemble_prediction(self, digits, prices, balance, base_stake):
        """Get prediction from ensemble of models"""
        if not digits or not prices:
            return self._default_prediction()

        # Get predictions from different models
        transformer_pred = self.transformer_predictor.predict_next_digit(digits)

        # For now, use transformer as primary, will integrate with existing LSTM later
        ensemble_pred = transformer_pred.copy()
        ensemble_pred['method'] = 'ensemble'

        # Boost confidence based on pattern strength
        pattern_strength = self._calculate_pattern_strength(digits)
        ensemble_pred['confidence'] = min(ensemble_pred['confidence'] * (1 + pattern_strength), 95)

        return ensemble_pred

    def _calculate_pattern_strength(self, digits):
        """Calculate strength of recent patterns"""
        if len(digits) < 10:
            return 0

        recent = digits[-10:]
        counter = Counter(recent)
        most_common = counter.most_common(1)[0]

        # Pattern strength based on frequency and consistency
        frequency = most_common[1] / len(recent)
        consistency = 1 - (len(counter) / 10)  # Fewer unique digits = more consistent

        return (frequency + consistency) / 2

    def _default_prediction(self):
        return {
            'predicted_digit': 5,
            'confidence': 10,
            'method': 'default'
        }

    def train_models(self, digits):
        """Train all models in ensemble"""
        return self.transformer_predictor.train(digits)

class AdaptivePredictor:
    """Adaptive predictor that adjusts based on market conditions"""

    def __init__(self):
        self.ensemble_predictor = EnsemblePredictor()
        self.market_regimes = {
            'trending': {'confidence_boost': 5, 'risk_multiplier': 1.2},
            'ranging': {'confidence_boost': 10, 'risk_multiplier': 0.8},
            'volatile': {'confidence_boost': -5, 'risk_multiplier': 0.6}
        }

    def detect_market_regime(self, prices):
        """Detect current market regime"""
        if len(prices) < 20:
            return 'ranging'

        # Calculate volatility
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)

        # Calculate trend strength
        trend = np.polyfit(range(len(prices)), prices, 1)[0]

        if volatility > 0.001:
            return 'volatile'
        elif abs(trend) > 0.0001:
            return 'trending'
        else:
            return 'ranging'

    def get_adaptive_prediction(self, digits, prices, balance, base_stake):
        """Get prediction with market regime adaptation"""
        # Get base ensemble prediction
        prediction = self.ensemble_predictor.get_ensemble_prediction(digits, prices, balance, base_stake)

        # Detect market regime
        regime = self.detect_market_regime(prices)

        # Apply regime-based adjustments
        regime_adjustments = self.market_regimes.get(regime, self.market_regimes['ranging'])

        prediction['confidence'] += regime_adjustments['confidence_boost']
        prediction['confidence'] = max(0, min(prediction['confidence'], 95))

        # Add regime information
        prediction['market_regime'] = regime
        prediction['regime_adjustments'] = regime_adjustments

        return prediction

    def train_models(self, digits):
        """Train all adaptive models"""
        return self.ensemble_predictor.train_models(digits)
