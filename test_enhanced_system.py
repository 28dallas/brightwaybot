#!/usr/bin/env python3
"""COMPREHENSIVE TESTING SCRIPT FOR ENHANCED TRADING SYSTEM"""

import sys
sys.path.append('./backend')

import asyncio
import numpy as np
from collections import deque
import json
from datetime import datetime, timedelta

# Import all enhanced components
from backend.ai_predictor import EnhancedPredictor
from backend.transformer_predictor import TransformerPredictor, EnsemblePredictor, AdaptivePredictor
from backend.ensemble_predictor import AdvancedEnsemblePredictor
from backend.adaptive_position_sizer import AdaptivePositionSizer, AdvancedRiskManager, MarketIntelligence

class EnhancedSystemTester:
    def __init__(self):
        self.test_results = {
            'matches_strategy': {},
            'hybrid_strategy': {},
            'ai_enhancements': {},
            'risk_management': {},
            'overall_performance': {}
        }

        # Initialize all components
        self.ai_predictor = EnhancedPredictor()
        self.transformer_predictor = TransformerPredictor()
        self.ensemble_predictor = AdvancedEnsemblePredictor()
        self.adaptive_predictor = AdaptivePredictor()
        self.position_sizer = AdaptivePositionSizer()
        self.risk_manager = AdvancedRiskManager()
        self.market_intelligence = MarketIntelligence()

    def generate_test_data(self, num_ticks=500):
        """Generate realistic test data for validation"""
        print("📊 Generating test data...")

        # Generate price data with realistic patterns
        base_price = 1234.56
        prices = []
        digits = []

        for i in range(num_ticks):
            # Add some trend and volatility
            trend = np.sin(i * 0.01) * 0.1
            noise = np.random.normal(0, 0.5)
            price = base_price + trend + noise

            # Extract digit from price
            digit = int(str(price).replace(".", "")[-1])

            prices.append(price)
            digits.append(digit)

        return digits, prices

    async def test_matches_strategy(self):
        """Test MATCHES strategy enhancements"""
        print("🧪 Testing MATCHES Strategy...")

        digits, prices = self.generate_test_data(300)

        # Test AI predictions
        predictions = []
        for i in range(50, len(digits)):
            recent_digits = digits[:i]
            recent_prices = prices[:i]

            try:
                prediction = self.ai_predictor.get_comprehensive_prediction(
                    recent_digits, recent_prices, 1000, 1.0
                )
                predictions.append(prediction)
            except Exception as e:
                print(f"❌ MATCHES prediction error: {e}")
                continue

        # Analyze results
        if predictions:
            avg_confidence = np.mean([p['final_confidence'] for p in predictions])
            high_confidence_preds = [p for p in predictions if p['final_confidence'] >= 75]

            self.test_results['matches_strategy'] = {
                'total_predictions': len(predictions),
                'avg_confidence': avg_confidence,
                'high_confidence_rate': len(high_confidence_preds) / len(predictions),
                'status': 'PASSED' if avg_confidence > 60 else 'FAILED'
            }

        print(f"   ✅ MATCHES Strategy: {self.test_results['matches_strategy']['status']}")

    async def test_hybrid_strategy(self):
        """Test hybrid DIFFERS + MATCHES strategy"""
        print("🧪 Testing Hybrid Strategy...")

        digits, prices = self.generate_test_data(400)

        # Test strategy selection
        strategy_selections = []
        for i in range(100, len(digits)):
            recent_digits = digits[:i]
            recent_prices = prices[:i]

            try:
                prediction = self.ai_predictor.get_comprehensive_prediction(
                    recent_digits, recent_prices, 1000, 1.0
                )

                # Simulate strategy selection
                confidence = prediction['final_confidence']
                if confidence >= 75:
                    strategy = 'MATCHES'
                elif confidence >= 70:
                    strategy = 'DIFFERS'
                else:
                    strategy = 'WAIT'

                strategy_selections.append(strategy)
            except Exception as e:
                print(f"❌ Hybrid strategy error: {e}")
                continue

        # Analyze strategy distribution
        if strategy_selections:
            strategy_counts = {}
            for strategy in strategy_selections:
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

            self.test_results['hybrid_strategy'] = {
                'total_decisions': len(strategy_selections),
                'matches_decisions': strategy_counts.get('MATCHES', 0),
                'differs_decisions': strategy_counts.get('DIFFERS', 0),
                'wait_decisions': strategy_counts.get('WAIT', 0),
                'strategy_diversity': len([s for s in strategy_counts.values() if s > 0]),
                'status': 'PASSED' if len(strategy_counts) >= 2 else 'FAILED'
            }

        print(f"   ✅ Hybrid Strategy: {self.test_results['hybrid_strategy']['status']}")

    async def test_ai_enhancements(self):
        """Test AI prediction enhancements"""
        print("🧪 Testing AI Enhancements...")

        digits, prices = self.generate_test_data(500)

        # Test transformer model
        transformer_predictions = []
        for i in range(100, len(digits)):
            recent_digits = digits[:i]

            try:
                prediction = self.transformer_predictor.predict_next_digit(recent_digits)
                transformer_predictions.append(prediction)
            except Exception as e:
                print(f"❌ Transformer prediction error: {e}")
                continue

        # Test ensemble predictions
        ensemble_predictions = []
        for i in range(100, len(digits)):
            recent_digits = digits[:i]
            recent_prices = prices[:i]

            try:
                prediction = self.ensemble_predictor.get_comprehensive_prediction(
                    recent_digits, recent_prices, 1000, 1.0
                )
                ensemble_predictions.append(prediction)
            except Exception as e:
                print(f"❌ Ensemble prediction error: {e}")
                continue

        # Test adaptive predictions
        adaptive_predictions = []
        for i in range(100, len(digits)):
            recent_digits = digits[:i]
            recent_prices = prices[:i]

            try:
                prediction = self.adaptive_predictor.get_adaptive_prediction(
                    recent_digits, recent_prices, 1000, 1.0
                )
                adaptive_predictions.append(prediction)
            except Exception as e:
                print(f"❌ Adaptive prediction error: {e}")
                continue

        # Analyze AI performance
        all_predictions = {
            'transformer': transformer_predictions,
            'ensemble': ensemble_predictions,
            'adaptive': adaptive_predictions
        }

        ai_results = {}
        for model_name, predictions in all_predictions.items():
            if predictions:
                avg_confidence = np.mean([p['confidence'] for p in predictions])
                high_confidence_rate = len([p for p in predictions if p['confidence'] >= 70]) / len(predictions)

                ai_results[model_name] = {
                    'predictions': len(predictions),
                    'avg_confidence': avg_confidence,
                    'high_confidence_rate': high_confidence_rate
                }

        self.test_results['ai_enhancements'] = {
            'models_tested': len(ai_results),
            'model_results': ai_results,
            'status': 'PASSED' if len(ai_results) >= 2 else 'FAILED'
        }

        print(f"   ✅ AI Enhancements: {self.test_results['ai_enhancements']['status']}")

    async def test_risk_management(self):
        """Test advanced risk management"""
        print("🧪 Testing Risk Management...")

        # Test position sizing
        test_scenarios = [
            {'balance': 1000, 'confidence': 80, 'volatility': 0.0005, 'regime': 'ranging'},
            {'balance': 1000, 'confidence': 70, 'volatility': 0.002, 'regime': 'volatile'},
            {'balance': 500, 'confidence': 85, 'volatility': 0.001, 'regime': 'trending'},
            {'balance': 2000, 'confidence': 60, 'volatility': 0.0008, 'regime': 'normal'}
        ]

        position_sizes = []
        for scenario in test_scenarios:
            try:
                position = self.position_sizer.calculate_optimal_position(
                    scenario['balance'],
                    scenario['confidence'],
                    scenario['volatility'],
                    scenario['regime']
                )
                position_sizes.append(position)
            except Exception as e:
                print(f"❌ Position sizing error: {e}")
                continue

        # Test risk limits
        risk_checks = []
        for i, scenario in enumerate(test_scenarios):
            try:
                allowed, reason = self.risk_manager.should_allow_trade(
                    scenario['balance'],
                    scenario['confidence'],
                    scenario['volatility'],
                    'MATCHES'
                )
                risk_checks.append(allowed)
            except Exception as e:
                print(f"❌ Risk check error: {e}")
                continue

        # Analyze risk management
        avg_position = np.mean(position_sizes) if position_sizes else 0
        risk_approval_rate = np.mean(risk_checks) if risk_checks else 0

        self.test_results['risk_management'] = {
            'scenarios_tested': len(test_scenarios),
            'avg_position_size': avg_position,
            'risk_approval_rate': risk_approval_rate,
            'position_variability': np.std(position_sizes) if position_sizes else 0,
            'status': 'PASSED' if (risk_approval_rate > 0.5 and len(position_sizes) == len(test_scenarios)) else 'FAILED'
        }

        print(f"   ✅ Risk Management: {self.test_results['risk_management']['status']}")

    async def test_market_intelligence(self):
        """Test market intelligence features"""
        print("🧪 Testing Market Intelligence...")

        digits, prices = self.generate_test_data(300)

        # Test market analysis
        try:
            market_analysis = self.market_intelligence.analyze_market_conditions(prices, digits)

            # Validate analysis structure
            required_keys = ['regime', 'sentiment', 'event_impact', 'recommendation', 'confidence_multiplier']
            analysis_complete = all(key in market_analysis for key in required_keys)

            # Test regime detection
            valid_regimes = ['trending', 'ranging', 'volatile', 'normal']
            regime_valid = market_analysis.get('regime') in valid_regimes

            # Test sentiment analysis
            valid_sentiments = ['bullish', 'bearish', 'neutral']
            sentiment_valid = market_analysis.get('sentiment') in valid_sentiments

            self.test_results['market_intelligence'] = {
                'analysis_complete': analysis_complete,
                'regime_valid': regime_valid,
                'sentiment_valid': sentiment_valid,
                'regime_detected': market_analysis.get('regime'),
                'sentiment_detected': market_analysis.get('sentiment'),
                'status': 'PASSED' if (analysis_complete and regime_valid and sentiment_valid) else 'FAILED'
            }

        except Exception as e:
            print(f"❌ Market intelligence error: {e}")
            self.test_results['market_intelligence'] = {
                'status': 'FAILED',
                'error': str(e)
            }

        print(f"   ✅ Market Intelligence: {self.test_results['market_intelligence']['status']}")

    async def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 STARTING COMPREHENSIVE ENHANCED SYSTEM TESTING")
        print("=" * 60)

        # Run all test suites
        await self.test_matches_strategy()
        await self.test_hybrid_strategy()
        await self.test_ai_enhancements()
        await self.test_risk_management()
        await self.test_market_intelligence()

        # Calculate overall results
        passed_tests = sum(1 for test in self.test_results.values() if test.get('status') == 'PASSED')
        total_tests = len(self.test_results)

        self.test_results['overall_performance'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests,
            'overall_status': 'PASSED' if passed_tests >= total_tests * 0.8 else 'FAILED'
        }

        # Print detailed results
        self.print_test_report()

        return self.test_results['overall_performance']['overall_status'] == 'PASSED'

    def print_test_report(self):
        """Print comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)

        for test_name, results in self.test_results.items():
            if test_name == 'overall_performance':
                continue

            print(f"\n🔍 {test_name.upper()} TEST:")
            print("-" * 40)

            if 'status' in results:
                status_icon = "✅" if results['status'] == 'PASSED' else "❌"
                print(f"Status: {status_icon} {results['status']}")

            for key, value in results.items():
                if key != 'status' and key != 'model_results':
                    if isinstance(value, float):
                        print(f"{key.replace('_', ' ').title()}: {value:.3f}")
                    else:
                        print(f"{key.replace('_', ' ').title()}: {value}")

            # Print model-specific results for AI tests
            if test_name == 'ai_enhancements' and 'model_results' in results:
                print("   Model Details:")
                for model, stats in results['model_results'].items():
                    print(f"     {model}: {stats['predictions']} predictions, {stats['avg_confidence']:.1f}% avg confidence")

        # Overall results
        overall = self.test_results['overall_performance']
        print(f"\n🎯 OVERALL RESULTS:")
        print("-" * 40)
        print(f"Total Tests: {overall['total_tests']}")
        print(f"Passed: {overall['passed_tests']}")
        print(f"Failed: {overall['failed_tests']}")
        print(f"Success Rate: {overall['success_rate']:.1%}")
        print(f"Overall Status: {'✅ PASSED' if overall['overall_status'] == 'PASSED' else '❌ FAILED'}")

        # Save results to file
        with open('enhanced_system_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)

        print("\n📄 Test results saved to 'enhanced_system_test_results.json'")
        print("\n🎉 Enhanced system testing completed!")
async def main():
    """Run comprehensive testing of enhanced system"""
    print("🤖 ENHANCED DERIV TRADING SYSTEM - COMPREHENSIVE TESTING")
    print("=" * 65)
    print("Testing all new features:")
    print("  • MATCHES Trading Strategy")
    print("  • Hybrid DIFFERS + MATCHES System")
    print("  • Advanced AI Ensemble Models")
    print("  • Adaptive Risk Management")
    print("  • Market Intelligence")
    print("=" * 65)

    tester = EnhancedSystemTester()

    try:
        success = await tester.run_comprehensive_test()

        if success:
            print("\n🎉 ALL TESTS PASSED! Enhanced system is ready for production.")
        else:
            print("\n⚠️ Some tests failed. Please review the results and fix issues.")

    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        print("Please check the system components and try again.")

if __name__ == "__main__":
    asyncio.run(main())
