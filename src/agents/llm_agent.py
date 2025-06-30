"""
LLM Agent for Multi-Market Correlation Engine
============================================

Intelligent agent that provides AI-powered financial analysis, insights,
and natural language interface using Llama LLM integration.

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
from typing import Dict, List, Any, Optional
import json
import threading

from .base_agent import BaseAgent, Task, TaskPriority, AgentStatus
from ..data.database_manager import DatabaseManager
from ..data.vector_database import get_vector_db
from ..models.llm_engine import get_llm_engine


class LLMAgent(BaseAgent):
    """
    Agent responsible for AI-powered financial analysis and insights.
    
    Features:
    - Natural language market analysis
    - Correlation pattern insights
    - Investment recommendation explanations
    - Anomaly detection analysis
    - Market regime commentary
    - Conversational query interface
    """
    
    def __init__(self, agent_id: str = "llm-agent-001", 
                 name: str = "LLM Agent", 
                 config: Optional[Dict] = None):
        """
        Initialize the LLM agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            config: Configuration dictionary
        """
        default_config = {
            'analysis_interval': 1800,  # 30 minutes
            'max_analysis_history': 100,
            'enable_auto_insights': True,
            'insight_triggers': [
                'correlation_change',
                'regime_change',
                'anomaly_detection',
                'portfolio_alert'
            ],
            'response_max_length': 512,
            'analysis_depth': 'comprehensive',
            'enable_chat_interface': True
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(agent_id, name, default_config)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.vector_db = get_vector_db()
        self.llm_engine = get_llm_engine()
        
        # Agent state
        self.analysis_history = []
        self.active_insights = {}
        self.last_analysis_time = None
        self.conversation_context = {}
        
        self.logger.info("LLM Agent initialized")
    
    def _handle_task(self, task: Task) -> Dict[str, Any]:
        """Handle incoming tasks."""
        task_type = task.data.get('type', 'unknown')
        
        self.logger.info(f"Handling LLM task: {task_type}")
        
        try:
            if task_type == 'generate_market_analysis':
                return self._generate_market_analysis_task(task.data)
            elif task_type == 'explain_correlations':
                return self._explain_correlations_task(task.data)
            elif task_type == 'explain_recommendations':
                return self._explain_recommendations_task(task.data)
            elif task_type == 'analyze_anomaly':
                return self._analyze_anomaly_task(task.data)
            elif task_type == 'analyze_regime_change':
                return self._analyze_regime_change_task(task.data)
            elif task_type == 'chat_query':
                return self._chat_query_task(task.data)
            elif task_type == 'generate_insights':
                return self._generate_insights_task(task.data)
            elif task_type == 'similarity_search':
                return self._similarity_search_task(task.data)
            else:
                return {'error': f'Unknown task type: {task_type}'}
                
        except Exception as e:
            self.logger.error(f"Task handling failed: {e}")
            return {'error': str(e)}
    
    def _generate_market_analysis_task(self, task_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive market analysis."""
        try:
            # Get market data
            symbols = task_data.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
            time_period = task_data.get('time_period', '1M')
            
            self.logger.info(f"Generating market analysis for {len(symbols)} symbols")
            
            # Collect market data
            market_data = self.db_manager.get_market_data(symbols=symbols)
            
            if market_data.empty:
                return {'error': 'No market data available'}
            
            # Prepare analysis data
            analysis_data = self._prepare_market_data_for_analysis(market_data, symbols)
            
            # Generate LLM analysis
            context = f"Market analysis for {time_period} period"
            analysis_result = self.llm_engine.generate_market_analysis(
                data=analysis_data,
                context=context
            )
            
            if 'error' not in analysis_result:
                # Store in vector database for future similarity search
                self._store_analysis_in_vector_db(analysis_result, symbols, 'market_analysis')
                
                # Add to history
                self.analysis_history.append(analysis_result)
                self._trim_analysis_history()
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Market analysis failed: {e}")
            return {'error': str(e)}
    
    def _explain_correlations_task(self, task_data: Dict) -> Dict[str, Any]:
        """Explain correlation patterns using LLM."""
        try:
            correlation_matrix = task_data.get('correlation_matrix')
            time_period = task_data.get('time_period', 'recent')
            
            if correlation_matrix is None:
                return {'error': 'No correlation matrix provided'}
            
            # Convert to DataFrame if needed
            if isinstance(correlation_matrix, dict):
                correlation_matrix = pd.DataFrame(correlation_matrix)
            
            self.logger.info(f"Explaining correlations for {len(correlation_matrix.columns)} assets")
            
            # Generate correlation insights
            insights = self.llm_engine.explain_correlations(
                correlation_matrix=correlation_matrix,
                time_period=time_period
            )
            
            if 'error' not in insights:
                # Store insights
                symbols = list(correlation_matrix.columns)
                self._store_analysis_in_vector_db(insights, symbols, 'correlation_insights')
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Correlation explanation failed: {e}")
            return {'error': str(e)}
    
    def _explain_recommendations_task(self, task_data: Dict) -> Dict[str, Any]:
        """Explain investment recommendations."""
        try:
            recommendations = task_data.get('recommendations', {})
            portfolio = task_data.get('portfolio', {})
            market_conditions = task_data.get('market_conditions', '')
            
            self.logger.info("Explaining investment recommendations")
            
            # Generate explanations
            explanations = self.llm_engine.explain_recommendations(
                recommendations=recommendations,
                portfolio=portfolio,
                market_conditions=market_conditions
            )
            
            if 'error' not in explanations:
                # Store explanations
                symbols = list(portfolio.keys())
                self._store_analysis_in_vector_db(explanations, symbols, 'recommendation_explanation')
            
            return explanations
            
        except Exception as e:
            self.logger.error(f"Recommendation explanation failed: {e}")
            return {'error': str(e)}
    
    def _analyze_anomaly_task(self, task_data: Dict) -> Dict[str, Any]:
        """Analyze market anomalies."""
        try:
            anomaly_data = task_data.get('anomaly_data', {})
            historical_context = task_data.get('historical_context', '')
            
            self.logger.info("Analyzing market anomaly")
            
            # Generate anomaly analysis
            analysis = self.llm_engine.analyze_anomaly(
                anomaly_data=anomaly_data,
                historical_context=historical_context
            )
            
            if 'error' not in analysis:
                # Store analysis
                symbols = anomaly_data.get('affected_symbols', [])
                self._store_analysis_in_vector_db(analysis, symbols, 'anomaly_analysis')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Anomaly analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_regime_change_task(self, task_data: Dict) -> Dict[str, Any]:
        """Analyze market regime changes."""
        try:
            regime_data = task_data.get('regime_data', {})
            transition_indicators = task_data.get('transition_indicators', {})
            
            self.logger.info("Analyzing regime change")
            
            # Generate regime analysis
            analysis = self.llm_engine.analyze_regime_change(
                regime_data=regime_data,
                transition_indicators=transition_indicators
            )
            
            if 'error' not in analysis:
                # Store analysis
                self._store_analysis_in_vector_db(analysis, [], 'regime_analysis')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Regime analysis failed: {e}")
            return {'error': str(e)}
    
    def _chat_query_task(self, task_data: Dict) -> Dict[str, Any]:
        """Handle conversational queries."""
        try:
            query = task_data.get('query', '')
            user_id = task_data.get('user_id', 'default')
            include_context = task_data.get('include_context', True)
            
            self.logger.info(f"Processing chat query: {query[:50]}...")
            
            # Prepare context
            context = None
            if include_context:
                context = self._get_conversation_context(user_id)
            
            # Generate response
            response = self.llm_engine.chat_query(query=query, context=context)
            
            if 'error' not in response:
                # Update conversation context
                self._update_conversation_context(user_id, query, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Chat query failed: {e}")
            return {'error': str(e)}
    
    def _generate_insights_task(self, task_data: Dict) -> Dict[str, Any]:
        """Generate automated insights based on triggers."""
        try:
            trigger_type = task_data.get('trigger_type', 'general')
            trigger_data = task_data.get('trigger_data', {})
            
            self.logger.info(f"Generating insights for trigger: {trigger_type}")
            
            insights = []
            
            if trigger_type == 'correlation_change':
                # Analyze correlation changes
                correlation_insight = self._analyze_correlation_change(trigger_data)
                if correlation_insight:
                    insights.append(correlation_insight)
            
            elif trigger_type == 'regime_change':
                # Analyze regime transitions
                regime_insight = self._analyze_regime_transition(trigger_data)
                if regime_insight:
                    insights.append(regime_insight)
            
            elif trigger_type == 'anomaly_detection':
                # Analyze detected anomalies
                anomaly_insight = self._analyze_detected_anomaly(trigger_data)
                if anomaly_insight:
                    insights.append(anomaly_insight)
            
            elif trigger_type == 'portfolio_alert':
                # Analyze portfolio alerts
                portfolio_insight = self._analyze_portfolio_alert(trigger_data)
                if portfolio_insight:
                    insights.append(portfolio_insight)
            
            return {
                'insights': insights,
                'trigger_type': trigger_type,
                'timestamp': datetime.now().isoformat(),
                'count': len(insights)
            }
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            return {'error': str(e)}
    
    def _similarity_search_task(self, task_data: Dict) -> Dict[str, Any]:
        """Perform similarity search in vector database."""
        try:
            query_type = task_data.get('query_type', 'text')
            query_data = task_data.get('query_data', '')
            k = task_data.get('k', 5)
            filters = task_data.get('filters', {})
            
            self.logger.info(f"Performing similarity search: {query_type}")
            
            if query_type == 'text':
                # Text-based similarity search
                results = self.vector_db.search_by_text_query(query_data, k=k)
            
            elif query_type == 'symbol_pattern':
                # Symbol pattern similarity
                symbol = query_data.get('symbol')
                price_data = query_data.get('price_data')
                results = self.vector_db.search_by_symbol_pattern(symbol, price_data, k=k)
            
            else:
                return {'error': f'Unknown query type: {query_type}'}
            
            # Apply additional filters
            if filters:
                results = self._apply_similarity_filters(results, filters)
            
            return {
                'results': results,
                'query_type': query_type,
                'count': len(results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return {'error': str(e)}
    
    def _prepare_market_data_for_analysis(self, market_data: pd.DataFrame, symbols: List[str]) -> Dict[str, Any]:
        """Prepare market data for LLM analysis."""
        try:
            analysis_data = {}
            
            # Basic statistics
            latest_data = market_data.groupby('symbol').last()
            analysis_data['latest_prices'] = latest_data['close'].to_dict()
            
            # Calculate returns
            returns_data = {}
            for symbol in symbols:
                symbol_data = market_data[market_data['symbol'] == symbol].sort_values('date')
                if len(symbol_data) > 1:
                    returns = symbol_data['close'].pct_change().dropna()
                    returns_data[symbol] = {
                        'mean_return': returns.mean(),
                        'volatility': returns.std(),
                        'recent_return': returns.iloc[-1] if len(returns) > 0 else 0
                    }
            
            analysis_data['returns_analysis'] = returns_data
            
            # Market summary
            analysis_data['market_summary'] = {
                'symbols_count': len(symbols),
                'data_points': len(market_data),
                'date_range': {
                    'start': market_data['date'].min().isoformat(),
                    'end': market_data['date'].max().isoformat()
                }
            }
            
            return analysis_data
            
        except Exception as e:
            self.logger.error(f"Error preparing market data: {e}")
            return {}
    
    def _store_analysis_in_vector_db(self, analysis: Dict[str, Any], symbols: List[str], analysis_type: str):
        """Store analysis results in vector database."""
        try:
            pattern_id = f"{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract text for embedding
            text_content = ""
            if 'analysis' in analysis:
                text_content = analysis['analysis']
            elif 'insights' in analysis:
                text_content = analysis['insights']
            elif 'explanation' in analysis:
                text_content = analysis['explanation']
            elif 'response' in analysis:
                text_content = analysis['response']
            
            # Store in vector database
            success = self.vector_db.add_financial_pattern(
                pattern_id=pattern_id,
                symbol=",".join(symbols) if symbols else "MARKET",
                pattern_type="composite_pattern",
                data={
                    'text_data': text_content,
                    'analysis_type': analysis_type,
                    'timestamp': analysis['timestamp']
                },
                metadata={
                    'analysis_type': analysis_type,
                    'symbols': symbols,
                    'timestamp': analysis['timestamp']
                }
            )
            
            if success:
                self.logger.info(f"Stored {analysis_type} analysis in vector database")
            
        except Exception as e:
            self.logger.error(f"Error storing analysis in vector DB: {e}")
    
    def _get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get conversation context for a user."""
        context = self.conversation_context.get(user_id, {})
        
        # Add recent analysis history
        recent_analyses = self.analysis_history[-5:] if self.analysis_history else []
        context['recent_analyses'] = [
            {
                'type': analysis.get('type', 'unknown'),
                'timestamp': analysis.get('timestamp'),
                'summary': analysis.get('analysis', '')[:200] + '...' if len(analysis.get('analysis', '')) > 200 else analysis.get('analysis', '')
            }
            for analysis in recent_analyses
        ]
        
        return context
    
    def _update_conversation_context(self, user_id: str, query: str, response: Dict[str, Any]):
        """Update conversation context."""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {'history': []}
        
        self.conversation_context[user_id]['history'].append({
            'query': query,
            'response': response.get('response', ''),
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_context[user_id]['history']) > 10:
            self.conversation_context[user_id]['history'] = self.conversation_context[user_id]['history'][-10:]
    
    def _trim_analysis_history(self):
        """Trim analysis history to max size."""
        if len(self.analysis_history) > self.config['max_analysis_history']:
            self.analysis_history = self.analysis_history[-self.config['max_analysis_history']:]
    
    def _analyze_correlation_change(self, trigger_data: Dict) -> Optional[Dict[str, Any]]:
        """Analyze correlation changes."""
        # Implementation for correlation change analysis
        return {
            'type': 'correlation_change_insight',
            'content': 'Significant correlation changes detected requiring portfolio review.',
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_regime_transition(self, trigger_data: Dict) -> Optional[Dict[str, Any]]:
        """Analyze regime transitions."""
        # Implementation for regime transition analysis
        return {
            'type': 'regime_transition_insight',
            'content': 'Market regime transition detected, consider defensive positioning.',
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_detected_anomaly(self, trigger_data: Dict) -> Optional[Dict[str, Any]]:
        """Analyze detected anomalies."""
        # Implementation for anomaly analysis
        return {
            'type': 'anomaly_insight',
            'content': 'Market anomaly detected, monitor for systemic risks.',
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_portfolio_alert(self, trigger_data: Dict) -> Optional[Dict[str, Any]]:
        """Analyze portfolio alerts."""
        # Implementation for portfolio alert analysis
        return {
            'type': 'portfolio_alert_insight',
            'content': 'Portfolio rebalancing recommended based on current market conditions.',
            'timestamp': datetime.now().isoformat()
        }
    
    def _apply_similarity_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to similarity search results."""
        filtered_results = results
        
        if 'min_similarity' in filters:
            min_sim = filters['min_similarity']
            filtered_results = [r for r in filtered_results if r.get('similarity_score', 0) >= min_sim]
        
        if 'symbols' in filters:
            symbol_filter = filters['symbols']
            filtered_results = [r for r in filtered_results if r.get('symbol') in symbol_filter]
        
        if 'analysis_type' in filters:
            type_filter = filters['analysis_type']
            filtered_results = [r for r in filtered_results if r.get('metadata', {}).get('analysis_type') == type_filter]
        
        return filtered_results
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        status = super().get_status()
        
        # Add LLM-specific metrics
        status.update({
            'llm_engine_available': self.llm_engine.get_model_info()['model_available'],
            'vector_db_patterns': self.vector_db.get_pattern_statistics()['total_patterns'],
            'analysis_history_count': len(self.analysis_history),
            'active_conversations': len(self.conversation_context),
            'last_analysis_time': self.last_analysis_time.isoformat() if self.last_analysis_time else None
        })
        
        return status
    
    def execute_task(self, task: Task) -> Any:
        """Execute a task (required by BaseAgent)."""
        return self._handle_task(task)


if __name__ == "__main__":
    # Test LLM agent functionality
    try:
        agent = LLMAgent()
        print("✅ LLM Agent initialized successfully!")
        
        # Test agent status
        status = agent.get_agent_status()
        print(f"📊 Agent status: {status}")
        
        # Test chat query
        from .base_agent import Task, TaskPriority
        
        task_data = {
            'type': 'chat_query',
            'query': 'What are the key principles of portfolio diversification?',
            'user_id': 'test_user'
        }
        
        task = Task(
            id="test_chat",
            name="chat_query",
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        result = agent._handle_task(task)
        print(f"💬 Chat result: {result}")
        
    except Exception as e:
        print(f"❌ LLM agent test failed: {e}") 