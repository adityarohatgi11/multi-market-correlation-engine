"""
Analysis Agent for Multi-Market Correlation Engine

This agent handles automated analysis tasks including correlation analysis,
GARCH modeling, VAR analysis, ML predictions, and regime detection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import threading

from .base_agent import BaseAgent, Task, TaskPriority, AgentStatus
from ..data.database_manager import DatabaseManager
from ..models.correlation_engine import CorrelationEngine
from ..models.garch_models import GARCHAnalyzer
from ..models.var_models import VARAnalyzer
from ..models.ml_models import MLCorrelationPredictor, RegimeDetector
from ..models.network_analysis import NetworkAnalyzer


class AnalysisAgent(BaseAgent):
    """
    Agent responsible for automated market analysis.
    
    Features:
    - Correlation analysis and monitoring
    - GARCH volatility modeling
    - VAR multivariate analysis
    - Machine learning predictions
    - Regime detection
    - Network analysis
    - Automated alerts and reporting
    """
    
    def __init__(self, agent_id: str = "analysis-agent-001", 
                 name: str = "Analysis Agent", 
                 config: Optional[Dict] = None):
        """
        Initialize the analysis agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            config: Configuration dictionary
        """
        default_config = {
            'analysis_interval': 3600,  # 1 hour
            'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
            'correlation_threshold': 0.7,
            'volatility_threshold': 0.05,
            'lookback_period': 252,  # 1 year of trading days
            'enable_ml_predictions': True,
            'enable_regime_detection': True,
            'enable_network_analysis': True,
            'alert_thresholds': {
                'high_correlation': 0.8,
                'high_volatility': 0.1,
                'regime_change': 0.8
            }
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(agent_id, name, default_config)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.correlation_engine = CorrelationEngine()
        self.garch_analyzer = GARCHAnalyzer()
        self.var_analyzer = VARAnalyzer()
        self.ml_predictor = MLCorrelationPredictor()
        self.regime_detector = RegimeDetector()
        self.network_analyzer = NetworkAnalyzer()
        
        # Analysis state
        self.last_analysis_time = None
        self.analysis_results = {}
        self.alerts = []
        self.model_cache = {}
        
        self.logger.info("Analysis Agent initialized")
    
    def execute_task(self, task: Task) -> Any:
        """Execute an analysis task"""
        task_type = task.data.get('type', 'unknown')
        
        try:
            if task_type == 'correlation_analysis':
                return self._perform_correlation_analysis(task.data)
            elif task_type == 'volatility_analysis':
                return self._perform_volatility_analysis(task.data)
            elif task_type == 'var_analysis':
                return self._perform_var_analysis(task.data)
            elif task_type == 'ml_prediction':
                return self._perform_ml_prediction(task.data)
            elif task_type == 'regime_detection':
                return self._perform_regime_detection(task.data)
            elif task_type == 'network_analysis':
                return self._perform_network_analysis(task.data)
            elif task_type == 'comprehensive_analysis':
                return self._perform_comprehensive_analysis(task.data)
            elif task_type == 'alert_check':
                return self._check_alerts(task.data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Analysis task execution failed: {e}")
            raise
    
    def _get_market_data(self, symbols: List[str], period_days: int = None) -> pd.DataFrame:
        """Get market data for analysis"""
        period_days = period_days or self.config['lookback_period']
        
        try:
            # Get data from database
            data = self.db_manager.get_market_data(
                symbols=symbols,
                start_date=datetime.now() - timedelta(days=period_days),
                end_date=datetime.now()
            )
            
            if data is None or data.empty:
                self.logger.warning(f"No data found for symbols: {symbols}")
                return pd.DataFrame()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error retrieving market data: {e}")
            raise
    
    def _perform_correlation_analysis(self, task_data: Dict) -> Dict[str, Any]:
        """Perform correlation analysis"""
        symbols = task_data.get('symbols', self.config['symbols'])
        window = task_data.get('window', 30)
        
        self.logger.info(f"Performing correlation analysis for {len(symbols)} symbols")
        
        try:
            # Get market data
            data = self._get_market_data(symbols)
            
            if data.empty:
                return {'error': 'No data available for analysis'}
            
            # Calculate correlations
            correlations = self.correlation_engine.calculate_rolling_correlations(
                data, window=window
            )
            
            # Calculate correlation matrix
            correlation_matrix, p_values = self.correlation_engine.calculate_correlation_matrix(data)
            
            # Extract correlation statistics from the matrix
            correlation_stats = {}
            if correlation_matrix is not None:
                # Handle both DataFrame and dict cases
                import numpy as np
                import pandas as pd
                
                if isinstance(correlation_matrix, pd.DataFrame) and not correlation_matrix.empty:
                    # Get upper triangle of correlation matrix (excluding diagonal)
                    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
                    correlations_upper = correlation_matrix.where(mask)
                    
                    # Convert to dictionary format
                    for i in range(len(correlation_matrix.columns)):
                        for j in range(i+1, len(correlation_matrix.columns)):
                            col_i = correlation_matrix.columns[i]
                            col_j = correlation_matrix.columns[j]
                            corr_value = correlation_matrix.iloc[i, j]
                            if not np.isnan(corr_value):
                                correlation_stats[f"{col_i}-{col_j}"] = corr_value
                elif isinstance(correlation_matrix, dict):
                    # If already a dict, use it directly
                    correlation_stats = correlation_matrix
            
            # Identify significant correlations
            significant_pairs = []
            threshold = self.config['correlation_threshold']
            
            for pair, corr_value in correlation_stats.items():
                if abs(corr_value) >= threshold:
                    significant_pairs.append({
                        'pair': pair,
                        'correlation': corr_value,
                        'strength': 'strong' if abs(corr_value) >= 0.8 else 'moderate'
                    })
            
            # Handle correlation matrix format
            matrix_dict = {}
            if correlation_matrix is not None:
                if isinstance(correlation_matrix, pd.DataFrame):
                    if not correlation_matrix.empty:
                        matrix_dict = correlation_matrix.to_dict()
                elif isinstance(correlation_matrix, dict):
                    matrix_dict = correlation_matrix
            
            results = {
                'symbols': symbols,
                'window': window,
                'correlation_matrix': matrix_dict,
                'correlation_stats': correlation_stats,
                'significant_pairs': significant_pairs,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Check for alerts
            self._check_correlation_alerts(significant_pairs)
            
            # Store results
            self.analysis_results['correlation'] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Correlation analysis failed: {e}")
            raise
    
    def _perform_volatility_analysis(self, task_data: Dict) -> Dict[str, Any]:
        """Perform GARCH volatility analysis"""
        symbols = task_data.get('symbols', self.config['symbols'])
        forecast_horizon = task_data.get('forecast_horizon', 5)
        
        self.logger.info(f"Performing volatility analysis for {len(symbols)} symbols")
        
        try:
            # Get market data
            data = self._get_market_data(symbols)
            
            if data.empty:
                return {'error': 'No data available for analysis'}
            
            volatility_results = {}
            
            for symbol in symbols:
                if symbol in data.columns:
                    symbol_data = data[symbol].dropna()
                    
                    if len(symbol_data) < 100:  # Minimum data requirement
                        continue
                    
                    # Fit GARCH model
                    model_results = self.garch_analyzer.fit_garch_model(symbol_data)
                    
                    # Generate forecasts
                    forecasts = self.garch_analyzer.forecast_volatility(
                        symbol_data, horizon=forecast_horizon
                    )
                    
                    volatility_results[symbol] = {
                        'current_volatility': model_results.get('current_volatility', 0),
                        'forecasts': forecasts,
                        'model_info': {
                            'aic': model_results.get('aic', 0),
                            'bic': model_results.get('bic', 0)
                        }
                    }
            
            results = {
                'symbols': symbols,
                'forecast_horizon': forecast_horizon,
                'volatility_analysis': volatility_results,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Check for volatility alerts
            self._check_volatility_alerts(volatility_results)
            
            # Store results
            self.analysis_results['volatility'] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Volatility analysis failed: {e}")
            raise
    
    def _perform_var_analysis(self, task_data: Dict) -> Dict[str, Any]:
        """Perform VAR multivariate analysis"""
        symbols = task_data.get('symbols', self.config['symbols'][:3])  # Limit for performance
        max_lags = task_data.get('max_lags', 5)
        
        self.logger.info(f"Performing VAR analysis for {len(symbols)} symbols")
        
        try:
            # Get market data
            data = self._get_market_data(symbols)
            
            if data.empty:
                return {'error': 'No data available for analysis'}
            
            # Prepare data for VAR
            var_data = data[symbols].dropna()
            
            if len(var_data) < 100:
                return {'error': 'Insufficient data for VAR analysis'}
            
            # Fit VAR model
            var_results = self.var_analyzer.fit_var_model(var_data, max_lags=max_lags)
            
            # Perform Granger causality tests
            causality_results = {}
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols):
                    if i != j:
                        causality = self.var_analyzer.granger_causality_test(
                            var_data, symbol1, symbol2
                        )
                        causality_results[f"{symbol1}_causes_{symbol2}"] = causality
            
            results = {
                'symbols': symbols,
                'max_lags': max_lags,
                'optimal_lags': var_results.get('optimal_lags', 1),
                'model_summary': var_results.get('summary', {}),
                'causality_tests': causality_results,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Store results
            self.analysis_results['var'] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"VAR analysis failed: {e}")
            raise
    
    def _perform_ml_prediction(self, task_data: Dict) -> Dict[str, Any]:
        """Perform machine learning predictions"""
        if not self.config['enable_ml_predictions']:
            return {'message': 'ML predictions disabled in config'}
        
        symbols = task_data.get('symbols', self.config['symbols'])
        prediction_horizon = task_data.get('horizon', 5)
        
        self.logger.info(f"Performing ML predictions for {len(symbols)} symbols")
        
        try:
            # Get market data
            data = self._get_market_data(symbols)
            
            if data.empty:
                return {'error': 'No data available for analysis'}
            
            # Train/update ML models
            training_results = self.ml_predictor.train_models(data)
            
            # Generate predictions
            predictions = self.ml_predictor.predict_correlations(data, horizon=prediction_horizon)
            
            results = {
                'symbols': symbols,
                'prediction_horizon': prediction_horizon,
                'model_performance': training_results,
                'predictions': predictions,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Store results
            self.analysis_results['ml_predictions'] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"ML prediction failed: {e}")
            raise
    
    def _perform_regime_detection(self, task_data: Dict) -> Dict[str, Any]:
        """Perform market regime detection"""
        if not self.config['enable_regime_detection']:
            return {'message': 'Regime detection disabled in config'}
        
        symbols = task_data.get('symbols', self.config['symbols'])
        n_regimes = task_data.get('n_regimes', 3)
        
        self.logger.info(f"Performing regime detection for {len(symbols)} symbols")
        
        try:
            # Get market data
            data = self._get_market_data(symbols)
            
            if data.empty:
                return {'error': 'No data available for analysis'}
            
            # Detect regimes
            regime_results = self.regime_detector.detect_regimes(data, n_regimes=n_regimes)
            
            # Get current regime
            current_regime = regime_results.get('current_regime', 0)
            regime_probabilities = regime_results.get('regime_probabilities', [])
            
            results = {
                'symbols': symbols,
                'n_regimes': n_regimes,
                'current_regime': current_regime,
                'regime_probabilities': regime_probabilities,
                'regime_characteristics': regime_results.get('regime_stats', {}),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Check for regime change alerts
            self._check_regime_alerts(results)
            
            # Store results
            self.analysis_results['regime_detection'] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Regime detection failed: {e}")
            raise
    
    def _perform_network_analysis(self, task_data: Dict) -> Dict[str, Any]:
        """Perform network analysis"""
        if not self.config['enable_network_analysis']:
            return {'message': 'Network analysis disabled in config'}
        
        symbols = task_data.get('symbols', self.config['symbols'])
        threshold = task_data.get('threshold', 0.5)
        
        self.logger.info(f"Performing network analysis for {len(symbols)} symbols")
        
        try:
            # Get market data
            data = self._get_market_data(symbols)
            
            if data.empty:
                return {'error': 'No data available for analysis'}
            
            # Build correlation network
            network_results = self.network_analyzer.build_correlation_network(
                data, threshold=threshold
            )
            
            # Calculate network metrics
            network_metrics = self.network_analyzer.calculate_network_metrics(
                network_results['graph']
            )
            
            # Identify systemic risk nodes
            systemic_risk = self.network_analyzer.identify_systemic_risk_nodes(
                network_results['graph']
            )
            
            results = {
                'symbols': symbols,
                'threshold': threshold,
                'network_metrics': network_metrics,
                'systemic_risk_nodes': systemic_risk,
                'edge_count': network_results.get('edge_count', 0),
                'density': network_results.get('density', 0),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Store results
            self.analysis_results['network_analysis'] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            raise
    
    def _perform_comprehensive_analysis(self, task_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive analysis combining all methods"""
        symbols = task_data.get('symbols', self.config['symbols'])
        
        self.logger.info(f"Performing comprehensive analysis for {len(symbols)} symbols")
        
        comprehensive_results = {}
        
        # Run all analysis types
        analysis_types = [
            ('correlation_analysis', {'symbols': symbols}),
            ('volatility_analysis', {'symbols': symbols}),
            ('var_analysis', {'symbols': symbols[:3]}),  # Limit for performance
        ]
        
        if self.config['enable_ml_predictions']:
            analysis_types.append(('ml_prediction', {'symbols': symbols}))
        
        if self.config['enable_regime_detection']:
            analysis_types.append(('regime_detection', {'symbols': symbols}))
        
        if self.config['enable_network_analysis']:
            analysis_types.append(('network_analysis', {'symbols': symbols}))
        
        for analysis_type, analysis_data in analysis_types:
            try:
                task = Task(
                    id=f"comp_{analysis_type}",
                    name=f"Comprehensive {analysis_type}",
                    priority=TaskPriority.MEDIUM,
                    created_at=datetime.now(),
                    scheduled_at=datetime.now(),
                    data={'type': analysis_type, **analysis_data}
                )
                
                result = self.execute_task(task)
                comprehensive_results[analysis_type] = result
                
            except Exception as e:
                self.logger.error(f"Failed to run {analysis_type}: {e}")
                comprehensive_results[analysis_type] = {'error': str(e)}
        
        # Generate summary
        summary = self._generate_analysis_summary(comprehensive_results)
        
        results = {
            'symbols': symbols,
            'analysis_results': comprehensive_results,
            'summary': summary,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        self.last_analysis_time = datetime.now()
        
        # Send completion message
        self.send_message(
            'reporting-agent-001',
            'analysis_complete',
            {'summary': summary, 'timestamp': self.last_analysis_time.isoformat()}
        )
        
        return results
    
    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of analysis results"""
        summary = {
            'total_analyses': len(results),
            'successful_analyses': len([r for r in results.values() if 'error' not in r]),
            'key_findings': [],
            'alerts_generated': len(self.alerts),
            'recommendations': []
        }
        
        # Extract key findings from each analysis
        if 'correlation_analysis' in results and 'error' not in results['correlation_analysis']:
            corr_result = results['correlation_analysis']
            significant_pairs = corr_result.get('significant_pairs', [])
            if significant_pairs:
                summary['key_findings'].append(
                    f"Found {len(significant_pairs)} significant correlation pairs"
                )
        
        if 'volatility_analysis' in results and 'error' not in results['volatility_analysis']:
            vol_result = results['volatility_analysis']
            high_vol_symbols = [
                symbol for symbol, data in vol_result.get('volatility_analysis', {}).items()
                if data.get('current_volatility', 0) > self.config['volatility_threshold']
            ]
            if high_vol_symbols:
                summary['key_findings'].append(
                    f"High volatility detected in: {', '.join(high_vol_symbols)}"
                )
        
        if 'regime_detection' in results and 'error' not in results['regime_detection']:
            regime_result = results['regime_detection']
            current_regime = regime_result.get('current_regime', 0)
            summary['key_findings'].append(f"Current market regime: {current_regime}")
        
        return summary
    
    def _check_correlation_alerts(self, significant_pairs: List[Dict]):
        """Check for correlation-based alerts"""
        threshold = self.config['alert_thresholds']['high_correlation']
        
        for pair_info in significant_pairs:
            if abs(pair_info['correlation']) >= threshold:
                alert = {
                    'type': 'high_correlation',
                    'message': f"High correlation detected: {pair_info['pair']} ({pair_info['correlation']:.3f})",
                    'severity': 'high' if abs(pair_info['correlation']) >= 0.9 else 'medium',
                    'timestamp': datetime.now().isoformat(),
                    'data': pair_info
                }
                self.alerts.append(alert)
                self.logger.warning(alert['message'])
    
    def _check_volatility_alerts(self, volatility_results: Dict):
        """Check for volatility-based alerts"""
        threshold = self.config['alert_thresholds']['high_volatility']
        
        for symbol, vol_data in volatility_results.items():
            current_vol = vol_data.get('current_volatility', 0)
            if current_vol >= threshold:
                alert = {
                    'type': 'high_volatility',
                    'message': f"High volatility detected in {symbol}: {current_vol:.3f}",
                    'severity': 'high' if current_vol >= threshold * 2 else 'medium',
                    'timestamp': datetime.now().isoformat(),
                    'data': {'symbol': symbol, 'volatility': current_vol}
                }
                self.alerts.append(alert)
                self.logger.warning(alert['message'])
    
    def _check_regime_alerts(self, regime_results: Dict):
        """Check for regime change alerts"""
        # This is simplified - in practice, you'd compare with previous regime
        current_regime = regime_results.get('current_regime', 0)
        probabilities = regime_results.get('regime_probabilities', [])
        
        if probabilities and len(probabilities) > current_regime:
            regime_confidence = probabilities[current_regime]
            
            if regime_confidence >= self.config['alert_thresholds']['regime_change']:
                alert = {
                    'type': 'regime_change',
                    'message': f"Strong regime signal detected: Regime {current_regime} (confidence: {regime_confidence:.3f})",
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat(),
                    'data': regime_results
                }
                self.alerts.append(alert)
                self.logger.info(alert['message'])
    
    def _check_alerts(self, task_data: Dict) -> Dict[str, Any]:
        """Check and process alerts"""
        # Clean old alerts (older than 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        
        return {
            'total_alerts': len(self.alerts),
            'alerts_by_type': self._group_alerts_by_type(),
            'recent_alerts': self.alerts[-10:],  # Last 10 alerts
            'timestamp': datetime.now().isoformat()
        }
    
    def _group_alerts_by_type(self) -> Dict[str, int]:
        """Group alerts by type"""
        alert_counts = {}
        for alert in self.alerts:
            alert_type = alert.get('type', 'unknown')
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        return alert_counts
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """Get detailed analysis status"""
        return {
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'available_results': list(self.analysis_results.keys()),
            'total_alerts': len(self.alerts),
            'alert_summary': self._group_alerts_by_type(),
            'model_cache_size': len(self.model_cache),
            'configured_symbols': self.config['symbols']
        }
    
    def force_analysis(self, analysis_type: str = 'comprehensive_analysis', 
                      symbols: Optional[List[str]] = None) -> str:
        """Force immediate analysis"""
        symbols = symbols or self.config['symbols']
        
        task = self.create_task(
            f"Manual {analysis_type}",
            {
                'type': analysis_type,
                'symbols': symbols
            },
            priority=TaskPriority.HIGH
        )
        
        return task.id


if __name__ == "__main__":
    # Test the analysis agent
    agent = AnalysisAgent()
    
    # Start the agent
    agent.start()
    
    # Force a comprehensive analysis
    task_id = agent.force_analysis('comprehensive_analysis', ['AAPL', 'MSFT'])
    print(f"Started analysis task: {task_id}")
    
    # Wait for task completion
    time.sleep(30)
    
    # Check status
    status = agent.get_analysis_status()
    print("Analysis Status:")
    print(f"Last analysis: {status['last_analysis']}")
    print(f"Available results: {status['available_results']}")
    print(f"Total alerts: {status['total_alerts']}")
    
    # Stop the agent
    agent.stop()