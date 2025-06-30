"""
Recommendation Agent for Multi-Market Correlation Engine
======================================================

Agent responsible for generating asset recommendations and portfolio optimization.
Integrates correlation analysis, ML predictions, and risk management.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
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
from ..models.recommendation_engine import AssetRecommendationEngine, PortfolioOptimizer


class RecommendationAgent(BaseAgent):
    """
    Agent responsible for asset recommendations and portfolio optimization.
    
    Features:
    - Multi-factor asset scoring
    - Portfolio optimization
    - Risk-adjusted recommendations
    - Regime-aware allocation
    - Real-time rebalancing alerts
    - Performance tracking
    """
    
    def __init__(self, agent_id: str = "recommendation-agent-001", 
                 name: str = "Recommendation Agent", 
                 config: Optional[Dict] = None):
        """
        Initialize the recommendation agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            config: Configuration dictionary
        """
        default_config = {
            'recommendation_interval': 3600,  # 1 hour
            'universe': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V'],
            'default_strategy': 'balanced',
            'default_horizon': '1M',
            'enable_auto_rebalancing': True,
            'rebalance_threshold': 0.05,
            'max_recommendations_per_run': 20,
            'enable_risk_monitoring': True,
            'portfolio_tracking': True,
            'performance_benchmark': 'SPY'
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(agent_id, name, default_config)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.recommendation_engine = AssetRecommendationEngine()
        self.portfolio_optimizer = PortfolioOptimizer()
        
        # Agent state
        self.last_recommendation_time = None
        self.current_recommendations = {}
        self.portfolio_history = []
        self.performance_metrics = {}
        self.active_portfolios = {}  # Track multiple portfolios
        
        self.logger.info("Recommendation Agent initialized")
    
    def _handle_task(self, task: Task) -> Dict[str, Any]:
        """Handle incoming tasks."""
        task_type = task.data.get('type', 'unknown')
        
        self.logger.info(f"Handling task: {task_type}")
        
        try:
            if task_type == 'generate_recommendations':
                return self._generate_recommendations_task(task.data)
            elif task_type == 'optimize_portfolio':
                return self._optimize_portfolio_task(task.data)
            elif task_type == 'analyze_portfolio':
                return self._analyze_portfolio_task(task.data)
            elif task_type == 'rebalance_check':
                return self._rebalance_check_task(task.data)
            elif task_type == 'performance_analysis':
                return self._performance_analysis_task(task.data)
            elif task_type == 'risk_assessment':
                return self._risk_assessment_task(task.data)
            else:
                return {'error': f'Unknown task type: {task_type}'}
                
        except Exception as e:
            self.logger.error(f"Task handling failed: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations_task(self, task_data: Dict) -> Dict[str, Any]:
        """Generate asset recommendations."""
        portfolio = task_data.get('portfolio', {})
        universe = task_data.get('universe', self.config['universe'])
        strategy = task_data.get('strategy', self.config['default_strategy'])
        horizon = task_data.get('horizon', self.config['default_horizon'])
        
        self.logger.info(f"Generating recommendations for {len(universe)} assets")
        
        try:
            # Generate recommendations
            recommendations = self.recommendation_engine.generate_recommendations(
                portfolio=portfolio,
                universe=universe,
                horizon=horizon,
                strategy=strategy
            )
            
            if 'error' not in recommendations:
                # Store recommendations
                self.current_recommendations = recommendations
                self.last_recommendation_time = datetime.now()
                
                # Generate summary
                summary = self.recommendation_engine.get_recommendation_summary(recommendations)
                recommendations['summary'] = summary
                
                # Track performance
                if self.config['portfolio_tracking']:
                    self._track_recommendation_performance(recommendations)
                
                self.logger.info(f"Generated {len(recommendations.get('buy_signals', []))} recommendations")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return {'error': str(e)}
    
    def _optimize_portfolio_task(self, task_data: Dict) -> Dict[str, Any]:
        """Optimize portfolio allocation."""
        portfolio = task_data.get('portfolio', {})
        optimization_method = task_data.get('method', 'mean_variance')
        target_return = task_data.get('target_return', None)
        
        self.logger.info(f"Optimizing portfolio using {optimization_method}")
        
        try:
            # Get market data for portfolio assets
            symbols = list(portfolio.keys())
            market_data = self.db_manager.get_market_data(symbols=symbols)
            
            if market_data.empty:
                return {'error': 'No market data available for optimization'}
            
            # Pivot data for optimization
            pivot_data = market_data.pivot(index='date', columns='symbol', values='close')
            returns = pivot_data.pct_change().dropna()
            
            if returns.empty:
                return {'error': 'Insufficient return data for optimization'}
            
            # Perform optimization
            if optimization_method == 'mean_variance':
                optimal_weights = self.portfolio_optimizer.mean_variance_optimization(
                    returns, target_return=target_return
                )
            elif optimization_method == 'risk_parity':
                optimal_weights = self.portfolio_optimizer.risk_parity_optimization(returns)
            else:
                return {'error': f'Unknown optimization method: {optimization_method}'}
            
            if not optimal_weights:
                return {'error': 'Portfolio optimization failed'}
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(returns, optimal_weights)
            
            result = {
                'optimization_method': optimization_method,
                'optimal_weights': optimal_weights,
                'portfolio_metrics': portfolio_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Portfolio optimization failed: {e}")
            return {'error': str(e)}
    
    def _analyze_portfolio_task(self, task_data: Dict) -> Dict[str, Any]:
        """Analyze portfolio performance and characteristics."""
        portfolio = task_data.get('portfolio', {})
        benchmark = task_data.get('benchmark', self.config['performance_benchmark'])
        
        if not portfolio:
            return {'error': 'No portfolio provided for analysis'}
        
        self.logger.info(f"Analyzing portfolio with {len(portfolio)} assets")
        
        try:
            # Get market data
            symbols = list(portfolio.keys())
            market_data = self.db_manager.get_market_data(symbols=symbols)
            
            if market_data.empty:
                return {'error': 'No market data available for analysis'}
            
            # Pivot data
            pivot_data = market_data.pivot(index='date', columns='symbol', values='close')
            returns = pivot_data.pct_change().dropna()
            
            # Calculate portfolio returns
            portfolio_weights = pd.Series(portfolio)
            available_symbols = returns.columns.intersection(portfolio_weights.index)
            
            if len(available_symbols) == 0:
                return {'error': 'No matching symbols in market data'}
            
            aligned_weights = portfolio_weights[available_symbols]
            aligned_weights = aligned_weights / aligned_weights.sum()
            
            portfolio_returns = (returns[available_symbols] * aligned_weights).sum(axis=1)
            
            # Calculate comprehensive metrics
            analysis = self._calculate_comprehensive_portfolio_analysis(
                portfolio_returns, returns, portfolio, benchmark
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {e}")
            return {'error': str(e)}
    
    def _rebalance_check_task(self, task_data: Dict) -> Dict[str, Any]:
        """Check if portfolio needs rebalancing."""
        current_portfolio = task_data.get('current_portfolio', {})
        target_portfolio = task_data.get('target_portfolio', {})
        
        if not current_portfolio or not target_portfolio:
            return {'error': 'Both current and target portfolios required'}
        
        self.logger.info("Checking rebalancing requirements")
        
        try:
            rebalance_analysis = self._analyze_rebalancing_needs(
                current_portfolio, target_portfolio
            )
            
            return rebalance_analysis
            
        except Exception as e:
            self.logger.error(f"Rebalance check failed: {e}")
            return {'error': str(e)}
    
    def _performance_analysis_task(self, task_data: Dict) -> Dict[str, Any]:
        """Analyze recommendation performance."""
        portfolio_id = task_data.get('portfolio_id', 'default')
        start_date = task_data.get('start_date', None)
        end_date = task_data.get('end_date', None)
        
        self.logger.info(f"Analyzing performance for portfolio: {portfolio_id}")
        
        try:
            performance_analysis = self._analyze_recommendation_performance(
                portfolio_id, start_date, end_date
            )
            
            return performance_analysis
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
            return {'error': str(e)}
    
    def _risk_assessment_task(self, task_data: Dict) -> Dict[str, Any]:
        """Assess portfolio risk."""
        portfolio = task_data.get('portfolio', {})
        risk_measures = task_data.get('risk_measures', ['var', 'cvar', 'max_drawdown'])
        
        if not portfolio:
            return {'error': 'No portfolio provided for risk assessment'}
        
        self.logger.info(f"Assessing risk for portfolio with {len(portfolio)} assets")
        
        try:
            risk_assessment = self._calculate_portfolio_risk_metrics(portfolio, risk_measures)
            
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            return {'error': str(e)}
    
    def _calculate_portfolio_metrics(self, returns: pd.DataFrame, weights: Dict[str, float]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio metrics."""
        try:
            # Align weights with returns
            weight_series = pd.Series(weights)
            available_symbols = returns.columns.intersection(weight_series.index)
            
            if len(available_symbols) == 0:
                return {'error': 'No matching symbols'}
            
            aligned_weights = weight_series[available_symbols]
            aligned_weights = aligned_weights / aligned_weights.sum()
            
            # Portfolio returns
            portfolio_returns = (returns[available_symbols] * aligned_weights).sum(axis=1)
            
            # Calculate metrics
            annual_return = portfolio_returns.mean() * 252
            annual_volatility = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
            
            # Drawdown calculation
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Risk metrics
            var_95 = np.percentile(portfolio_returns, 5)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            
            # Correlation analysis
            correlation_matrix = returns[available_symbols].corr()
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            
            metrics = {
                'annual_return': annual_return,
                'annual_volatility': annual_volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'var_95': var_95,
                'cvar_95': cvar_95,
                'avg_correlation': avg_correlation,
                'diversification_ratio': 1 - avg_correlation,
                'number_of_assets': len(available_symbols),
                'concentration_risk': max(aligned_weights),
                'effective_assets': 1 / (aligned_weights ** 2).sum()  # Herfindahl index
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Portfolio metrics calculation failed: {e}")
            return {'error': str(e)}
    
    def _calculate_comprehensive_portfolio_analysis(self, portfolio_returns: pd.Series, 
                                                  asset_returns: pd.DataFrame, 
                                                  portfolio: Dict[str, float],
                                                  benchmark: str) -> Dict[str, Any]:
        """Calculate comprehensive portfolio analysis."""
        try:
            # Basic portfolio metrics
            annual_return = portfolio_returns.mean() * 252
            annual_volatility = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
            
            # Drawdown analysis
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Risk metrics
            var_95 = np.percentile(portfolio_returns, 5)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            
            # Asset contribution analysis
            portfolio_weights = pd.Series(portfolio)
            asset_contributions = {}
            
            for symbol in asset_returns.columns:
                if symbol in portfolio_weights.index:
                    weight = portfolio_weights[symbol]
                    asset_return = asset_returns[symbol].mean() * 252
                    contribution = weight * asset_return
                    asset_contributions[symbol] = {
                        'weight': weight,
                        'return_contribution': contribution,
                        'risk_contribution': weight * asset_returns[symbol].std() * np.sqrt(252)
                    }
            
            # Correlation analysis
            correlation_matrix = asset_returns.corr()
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_metrics': {
                    'annual_return': annual_return,
                    'annual_volatility': annual_volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_drawdown,
                    'var_95': var_95,
                    'cvar_95': cvar_95
                },
                'diversification_metrics': {
                    'avg_correlation': avg_correlation,
                    'diversification_ratio': 1 - avg_correlation,
                    'number_of_assets': len(portfolio),
                    'effective_assets': 1 / (portfolio_weights ** 2).sum(),
                    'concentration_risk': max(portfolio_weights)
                },
                'asset_contributions': asset_contributions,
                'risk_analysis': {
                    'total_risk': annual_volatility,
                    'systematic_risk': avg_correlation * annual_volatility,
                    'idiosyncratic_risk': (1 - avg_correlation) * annual_volatility
                }
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_rebalancing_needs(self, current_portfolio: Dict[str, float], 
                                 target_portfolio: Dict[str, float]) -> Dict[str, Any]:
        """Analyze rebalancing requirements."""
        try:
            all_symbols = set(list(current_portfolio.keys()) + list(target_portfolio.keys()))
            
            rebalancing_actions = []
            total_drift = 0.0
            
            for symbol in all_symbols:
                current_weight = current_portfolio.get(symbol, 0.0)
                target_weight = target_portfolio.get(symbol, 0.0)
                drift = target_weight - current_weight
                
                total_drift += abs(drift)
                
                if abs(drift) > self.config['rebalance_threshold']:
                    action_type = 'buy' if drift > 0 else 'sell'
                    if current_weight == 0:
                        action_type = 'new_position'
                    elif target_weight == 0:
                        action_type = 'exit_position'
                    
                    rebalancing_actions.append({
                        'symbol': symbol,
                        'current_weight': current_weight,
                        'target_weight': target_weight,
                        'drift': drift,
                        'action': action_type,
                        'urgency': 'high' if abs(drift) > 0.1 else 'medium'
                    })
            
            needs_rebalancing = total_drift > self.config['rebalance_threshold']
            
            analysis = {
                'needs_rebalancing': needs_rebalancing,
                'total_drift': total_drift,
                'rebalancing_actions': rebalancing_actions,
                'urgency': 'high' if total_drift > 0.2 else 'medium' if total_drift > 0.1 else 'low',
                'estimated_transaction_cost': len(rebalancing_actions) * 0.001,  # Rough estimate
                'recommendation': 'rebalance_now' if needs_rebalancing else 'monitor'
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Rebalancing analysis failed: {e}")
            return {'error': str(e)}
    
    def _track_recommendation_performance(self, recommendations: Dict[str, Any]):
        """Track recommendation performance over time."""
        try:
            tracking_data = {
                'timestamp': datetime.now().isoformat(),
                'recommendations': recommendations,
                'buy_signals_count': len(recommendations.get('buy_signals', [])),
                'sell_signals_count': len(recommendations.get('sell_signals', [])),
                'risk_level': recommendations.get('risk_assessment', {}).get('overall_risk_level', 'unknown')
            }
            
            self.portfolio_history.append(tracking_data)
            
            # Keep only last 100 recommendations
            if len(self.portfolio_history) > 100:
                self.portfolio_history = self.portfolio_history[-100:]
                
        except Exception as e:
            self.logger.error(f"Performance tracking failed: {e}")
    
    def _analyze_recommendation_performance(self, portfolio_id: str, 
                                         start_date: Optional[str], 
                                         end_date: Optional[str]) -> Dict[str, Any]:
        """Analyze historical recommendation performance."""
        try:
            # Filter portfolio history
            relevant_history = [
                entry for entry in self.portfolio_history
                if self._is_in_date_range(entry['timestamp'], start_date, end_date)
            ]
            
            if not relevant_history:
                return {'error': 'No historical data available for analysis'}
            
            # Calculate performance metrics
            total_recommendations = len(relevant_history)
            avg_buy_signals = np.mean([entry['buy_signals_count'] for entry in relevant_history])
            avg_sell_signals = np.mean([entry['sell_signals_count'] for entry in relevant_history])
            
            risk_distribution = {}
            for entry in relevant_history:
                risk_level = entry['risk_level']
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            analysis = {
                'portfolio_id': portfolio_id,
                'analysis_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_recommendations': total_recommendations
                },
                'recommendation_statistics': {
                    'avg_buy_signals': avg_buy_signals,
                    'avg_sell_signals': avg_sell_signals,
                    'total_signals': avg_buy_signals + avg_sell_signals
                },
                'risk_distribution': risk_distribution,
                'performance_summary': f"Generated {total_recommendations} recommendations with average {avg_buy_signals:.1f} buy signals"
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_portfolio_risk_metrics(self, portfolio: Dict[str, float], 
                                        risk_measures: List[str]) -> Dict[str, Any]:
        """Calculate detailed portfolio risk metrics."""
        try:
            # Get market data
            symbols = list(portfolio.keys())
            market_data = self.db_manager.get_market_data(symbols=symbols)
            
            if market_data.empty:
                return {'error': 'No market data available'}
            
            # Pivot and calculate returns
            pivot_data = market_data.pivot(index='date', columns='symbol', values='close')
            returns = pivot_data.pct_change().dropna()
            
            # Calculate portfolio returns
            portfolio_weights = pd.Series(portfolio)
            available_symbols = returns.columns.intersection(portfolio_weights.index)
            aligned_weights = portfolio_weights[available_symbols]
            aligned_weights = aligned_weights / aligned_weights.sum()
            
            portfolio_returns = (returns[available_symbols] * aligned_weights).sum(axis=1)
            
            risk_metrics = {}
            
            # Value at Risk (VaR)
            if 'var' in risk_measures:
                var_95 = np.percentile(portfolio_returns, 5)
                var_99 = np.percentile(portfolio_returns, 1)
                risk_metrics['var'] = {
                    'var_95': var_95,
                    'var_99': var_99,
                    'var_95_annualized': var_95 * np.sqrt(252)
                }
            
            # Conditional Value at Risk (CVaR)
            if 'cvar' in risk_measures:
                var_95 = np.percentile(portfolio_returns, 5)
                cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
                risk_metrics['cvar'] = {
                    'cvar_95': cvar_95,
                    'cvar_95_annualized': cvar_95 * np.sqrt(252)
                }
            
            # Maximum Drawdown
            if 'max_drawdown' in risk_measures:
                cumulative = (1 + portfolio_returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                max_drawdown = drawdown.min()
                risk_metrics['max_drawdown'] = {
                    'max_drawdown': max_drawdown,
                    'current_drawdown': drawdown.iloc[-1]
                }
            
            # Volatility metrics
            annual_volatility = portfolio_returns.std() * np.sqrt(252)
            risk_metrics['volatility'] = {
                'daily_volatility': portfolio_returns.std(),
                'annual_volatility': annual_volatility,
                'volatility_rank': 'high' if annual_volatility > 0.25 else 'medium' if annual_volatility > 0.15 else 'low'
            }
            
            # Risk assessment summary
            risk_score = self._calculate_composite_risk_score(risk_metrics)
            
            assessment = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_symbols': symbols,
                'risk_metrics': risk_metrics,
                'composite_risk_score': risk_score,
                'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
                'recommendations': self._generate_risk_recommendations(risk_metrics, risk_score)
            }
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Risk metrics calculation failed: {e}")
            return {'error': str(e)}
    
    def _calculate_composite_risk_score(self, risk_metrics: Dict[str, Any]) -> float:
        """Calculate composite risk score (0-1, higher is riskier)."""
        try:
            score = 0.0
            weight_sum = 0.0
            
            # Volatility component
            if 'volatility' in risk_metrics:
                vol = risk_metrics['volatility']['annual_volatility']
                vol_score = min(vol / 0.5, 1.0)  # Cap at 50% volatility
                score += vol_score * 0.4
                weight_sum += 0.4
            
            # VaR component
            if 'var' in risk_metrics:
                var_95 = abs(risk_metrics['var']['var_95'])
                var_score = min(var_95 / 0.05, 1.0)  # Cap at 5% daily VaR
                score += var_score * 0.3
                weight_sum += 0.3
            
            # Max drawdown component
            if 'max_drawdown' in risk_metrics:
                max_dd = abs(risk_metrics['max_drawdown']['max_drawdown'])
                dd_score = min(max_dd / 0.3, 1.0)  # Cap at 30% drawdown
                score += dd_score * 0.3
                weight_sum += 0.3
            
            return score / weight_sum if weight_sum > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {e}")
            return 0.5
    
    def _generate_risk_recommendations(self, risk_metrics: Dict[str, Any], risk_score: float) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []
        
        try:
            if risk_score > 0.7:
                recommendations.append("Consider reducing portfolio risk through diversification")
                recommendations.append("Implement stop-loss orders to limit downside risk")
            
            if 'volatility' in risk_metrics:
                vol = risk_metrics['volatility']['annual_volatility']
                if vol > 0.25:
                    recommendations.append("High volatility detected - consider defensive assets")
            
            if 'max_drawdown' in risk_metrics:
                max_dd = abs(risk_metrics['max_drawdown']['max_drawdown'])
                if max_dd > 0.2:
                    recommendations.append("Large drawdown risk - implement risk management rules")
            
            if not recommendations:
                recommendations.append("Risk levels are within acceptable ranges")
                
        except Exception as e:
            self.logger.error(f"Risk recommendations generation failed: {e}")
            recommendations.append("Unable to generate risk recommendations")
        
        return recommendations
    
    def _is_in_date_range(self, timestamp_str: str, start_date: Optional[str], end_date: Optional[str]) -> bool:
        """Check if timestamp is within date range."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            if start_date:
                start = datetime.fromisoformat(start_date)
                if timestamp < start:
                    return False
            
            if end_date:
                end = datetime.fromisoformat(end_date)
                if timestamp > end:
                    return False
            
            return True
            
        except Exception:
            return True  # Include if date parsing fails
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.name,
            'status': self.status.value,
            'last_recommendation_time': self.last_recommendation_time.isoformat() if self.last_recommendation_time else None,
            'active_recommendations': len(self.current_recommendations),
            'portfolio_history_count': len(self.portfolio_history),
            'config': self.config,
            'performance_metrics': self.performance_metrics
        }
    
    def run_periodic_tasks(self):
        """Run periodic recommendation tasks."""
        try:
            if self.config['enable_auto_rebalancing']:
                # Check for rebalancing opportunities
                self._check_auto_rebalancing()
            
            if self.config['enable_risk_monitoring']:
                # Monitor portfolio risks
                self._monitor_portfolio_risks()
                
        except Exception as e:
            self.logger.error(f"Periodic tasks failed: {e}")
    
    def _check_auto_rebalancing(self):
        """Check for automatic rebalancing opportunities."""
        # Implementation for automatic rebalancing checks
        pass
    
    def _monitor_portfolio_risks(self):
        """Monitor portfolio risk levels."""
        # Implementation for risk monitoring
        pass
    
    def execute_task(self, task):
        """Execute a task (required by BaseAgent)."""
        return self._handle_task(task) 