import unittest
from backend.ai_performance_monitor import AIPerformanceMonitor

class TestAIPerformanceMonitor(unittest.TestCase):
    def test_accuracy_calculation(self):
        monitor = AIPerformanceMonitor()
        predictions = [1, 2, 3, 4, 5]
        actuals = [1, 2, 0, 4, 5]

        for p, a in zip(predictions, actuals):
            monitor.log_prediction(p, a, confidence=80)

        accuracy = monitor.get_accuracy()
        self.assertAlmostEqual(accuracy, 80.0)

    def test_no_predictions(self):
        monitor = AIPerformanceMonitor()
        self.assertEqual(monitor.get_accuracy(), 0.0)

if __name__ == "__main__":
    unittest.main()
