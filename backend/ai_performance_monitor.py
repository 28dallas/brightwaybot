import logging
import numpy as np

class AIPerformanceMonitor:
    def __init__(self):
        self.predictions = []
        self.actuals = []
        self.accuracy = 0.0

    def log_prediction(self, predicted_digit, actual_digit, confidence):
        self.predictions.append(predicted_digit)
        self.actuals.append(actual_digit)
        self._update_accuracy()

        logging.info(f"Prediction: {predicted_digit}, Actual: {actual_digit}, Confidence: {confidence:.2f}%, Accuracy: {self.accuracy:.2f}%")

    def _update_accuracy(self):
        if not self.predictions or not self.actuals:
            self.accuracy = 0.0
            return

        correct = sum(p == a for p, a in zip(self.predictions, self.actuals))
        self.accuracy = (correct / len(self.predictions)) * 100

    def get_accuracy(self):
        return self.accuracy
