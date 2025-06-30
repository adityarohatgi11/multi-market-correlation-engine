#!/usr/bin/env python3
"""
Comprehensive test script for Phase 2: Advanced Analytics Components
Tests: Correlation Engine, GARCH Models, VAR Models, ML Models, Network Analysis
"""

import sys
import os
import traceback
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all Phase 2 imports"""
    print("=" * 60)
    print("TESTING PHASE 2 IMPORTS")
    print("=" * 60)
    
    imports_to_test = [
        ("correlation_engine", "CorrelationEngine"),
        ("garch_models", "GARCHAnalyzer"),
        ("var_models", "VARAnalyzer"),
        ("ml_models", "MLCorrelationPredictor"),
        ("network_analysis", "NetworkAnalyzer"),
        ("statistical_utils", "RiskMetrics")
    ]
    
    success_count = 0
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(f"src.models.{module_name}", fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {class_name} import successful")
            success_count += 1
        except Exception as e:
            print(f"❌ {class_name} import failed: {e}")
            traceback.print_exc()
    
    return success_count == len(imports_to_test)

def generate_test_data():
    """Generate synthetic test data for Phase 2 testing"""
    print("\n" + "=" * 60)
    print("GENERATING TEST DATA")
    print("=" * 60)
    
    try:
        # Generate 200 days of synthetic data for 5 symbols (more reasonable size)
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        np.random.seed(42)  # For reproducible results
        
        data = {}
        for symbol in symbols:
            # Generate more reasonable returns
            base_return = np.random.normal(0.0005, 0.015, len(dates))  # Smaller returns
            if symbol != 'AAPL':
                # Add correlation with AAPL
                correlation_factor = np.random.uniform(0.3, 0.7)
                base_return = correlation_factor * data.get('AAPL', base_return) + \
                             (1 - correlation_factor) * base_return
            
            # Convert to prices (starting at 100)
            prices = 100 * np.exp(np.cumsum(base_return))
            data[symbol] = prices
        
        df = pd.DataFrame(data, index=dates)
        print(f"✅ Generated test data: {df.shape[0]} days, {df.shape[1]} symbols")
        print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
        
        return df
        
    except Exception as e:
        print(f"❌ Test data generation failed: {e}")
        traceback.print_exc()
        return None

def test_correlation_engine(data):
    """Test CorrelationEngine functionality"""
    print("\n" + "=" * 60)
    print("TESTING CORRELATION ENGINE")
    print("=" * 60)
    
    try:
        from src.models.correlation_engine import CorrelationEngine
        
        engine = CorrelationEngine()
        print("✅ CorrelationEngine initialization successful")
        
        # Test correlation matrix calculation (returns tuple)
        corr_matrix, pval_matrix = engine.calculate_correlation_matrix(data)
        print(f"✅ Correlation matrix calculated: {corr_matrix.shape}")
        print(f"✅ P-value matrix calculated: {pval_matrix.shape}")
        
        # Test rolling correlations
        rolling_corrs = engine.calculate_rolling_correlations(data, window=20)
        print(f"✅ Rolling correlations calculated: {len(rolling_corrs)} pairs")
        
        # Test comprehensive analysis
        symbols = data.columns.tolist()
        comprehensive_results = engine.run_comprehensive_analysis(symbols)
        print("✅ Comprehensive correlation analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ CorrelationEngine test failed: {e}")
        traceback.print_exc()
        return False

def test_garch_models(data):
    """Test GARCH models functionality"""
    print("\n" + "=" * 60)
    print("TESTING GARCH MODELS")
    print("=" * 60)
    
    try:
        from src.models.garch_models import GARCHAnalyzer
        
        analyzer = GARCHAnalyzer()
        print("✅ GARCHAnalyzer initialization successful")
        
        # Test single symbol GARCH
        symbol = 'AAPL'
        returns = data[symbol].pct_change().dropna() * 100  # Convert to percentage
        
        garch_result = analyzer.fit_garch_model(returns)
        if garch_result:
            print(f"✅ GARCH model fitted for {symbol}")
            
            # Test volatility forecasting with fitted model
            forecast = analyzer.forecast_volatility(garch_result, horizon=5)
            if forecast:
                print(f"✅ Volatility forecast: {forecast['horizon']} steps")
            else:
                print("⚠️ Volatility forecast returned empty result")
        else:
            print("⚠️ GARCH model fitting returned empty result")
        
        # Test comprehensive analysis
        symbols = [symbol]  # Test with one symbol first
        comprehensive_results = analyzer.run_comprehensive_garch_analysis(symbols)
        print("✅ Comprehensive GARCH analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ GARCH models test failed: {e}")
        traceback.print_exc()
        return False

def test_var_models(data):
    """Test VAR models functionality"""
    print("\n" + "=" * 60)
    print("TESTING VAR MODELS")
    print("=" * 60)
    
    try:
        from src.models.var_models import VARAnalyzer
        
        analyzer = VARAnalyzer()
        print("✅ VARAnalyzer initialization successful")
        
        # Use smaller subset for VAR (VAR needs more observations per variable)
        symbols = ['AAPL', 'MSFT']  # Use only 2 symbols
        var_data = data[symbols]
        
        # Test comprehensive VAR analysis
        comprehensive_results = analyzer.run_comprehensive_var_analysis(symbols)
        print("✅ Comprehensive VAR analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ VAR models test failed: {e}")
        traceback.print_exc()
        return False

def test_ml_models(data):
    """Test ML models functionality"""
    print("\n" + "=" * 60)
    print("TESTING ML MODELS")
    print("=" * 60)
    
    try:
        from src.models.ml_models import MLCorrelationPredictor
        
        predictor = MLCorrelationPredictor()
        print("✅ MLCorrelationPredictor initialization successful")
        
        # Test feature preparation
        symbols = data.columns.tolist()
        X, y = predictor.prepare_ml_features(symbols)
        if not X.empty:
            print(f"✅ ML features prepared: {X.shape[1]} features, {X.shape[0]} samples")
        else:
            print("⚠️ No ML features prepared")
        
        # Test comprehensive ML analysis
        comprehensive_results = predictor.run_comprehensive_ml_analysis(symbols)
        print("✅ Comprehensive ML analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ ML models test failed: {e}")
        traceback.print_exc()
        return False

def test_network_analysis(data):
    """Test Network Analysis functionality"""
    print("\n" + "=" * 60)
    print("TESTING NETWORK ANALYSIS")
    print("=" * 60)
    
    try:
        from src.models.network_analysis import NetworkAnalyzer
        
        analyzer = NetworkAnalyzer()
        print("✅ NetworkAnalyzer initialization successful")
        
        # Prepare returns data for network analysis
        returns = data.pct_change().dropna()
        
        # Test correlation network creation
        network_result = analyzer.create_correlation_network(returns, threshold=0.1)  # Lower threshold
        if network_result:
            print(f"✅ Correlation network created: {network_result['n_nodes']} nodes, {network_result['n_edges']} edges")
            
            # Test network metrics
            metrics = network_result.get('metrics', {})
            if metrics:
                print(f"✅ Network metrics calculated: {len(metrics)} metrics")
            
            # Test systemic risk detection
            systemic_result = analyzer.detect_systemic_risk_nodes(network_result)
            if systemic_result:
                print("✅ Systemic risk nodes identified")
        else:
            print("⚠️ Network creation returned empty result")
        
        # Test comprehensive network analysis
        symbols = data.columns.tolist()
        comprehensive_results = analyzer.run_comprehensive_network_analysis(symbols)
        print("✅ Comprehensive network analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Network analysis test failed: {e}")
        traceback.print_exc()
        return False

def test_statistical_utils():
    """Test statistical utilities"""
    print("\n" + "=" * 60)
    print("TESTING STATISTICAL UTILITIES")
    print("=" * 60)
    
    try:
        from src.models.statistical_utils import RiskMetrics, DistributionAnalysis
        
        # Generate sample returns data
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 100))
        prices = pd.Series(100 * np.exp(np.cumsum(returns)))
        
        # Test RiskMetrics
        var = RiskMetrics.value_at_risk(returns)
        sharpe = RiskMetrics.sharpe_ratio(returns)
        drawdown = RiskMetrics.maximum_drawdown(prices)
        
        print(f"✅ VaR calculated: {var:.4f}")
        print(f"✅ Sharpe ratio calculated: {sharpe:.4f}")
        print(f"✅ Maximum drawdown: {drawdown['max_drawdown']:.4f}")
        
        # Test DistributionAnalysis
        moments = DistributionAnalysis.distribution_moments(returns)
        print(f"✅ Distribution moments calculated: {len(moments)} metrics")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistical utilities test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all Phase 2 tests"""
    print("PHASE 2 ADVANCED ANALYTICS TESTING")
    print("=" * 60)
    
    test_results = []
    
    # Test imports
    imports_success = test_imports()
    test_results.append(("Imports", imports_success))
    
    if not imports_success:
        print("❌ Imports failed, skipping other tests")
        return False
    
    # Generate test data
    test_data = generate_test_data()
    if test_data is None:
        print("❌ Test data generation failed, cannot continue")
        return False
    
    # Test each component
    test_results.append(("Correlation Engine", test_correlation_engine(test_data)))
    test_results.append(("GARCH Models", test_garch_models(test_data)))
    test_results.append(("VAR Models", test_var_models(test_data)))
    test_results.append(("ML Models", test_ml_models(test_data)))
    test_results.append(("Network Analysis", test_network_analysis(test_data)))
    test_results.append(("Statistical Utilities", test_statistical_utils()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("PHASE 2 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(test_results)} tests passed")
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 