"""
LLM and Vector Database API Endpoints
====================================

API endpoints for AI-powered financial analysis, insights generation,
and vector similarity search capabilities.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import pandas as pd

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.llm_engine import get_llm_engine
from src.data.vector_database import get_vector_db
from src.agents.llm_agent import LLMAgent
from src.agents.base_agent import Task, TaskPriority

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/llm", tags=["llm", "ai", "vector-search"])

# Initialize components
llm_engine = get_llm_engine()
vector_db = get_vector_db()
llm_agent = LLMAgent()


# Pydantic models for request/response
class MarketAnalysisRequest(BaseModel):
    symbols: List[str]
    time_period: Optional[str] = "1M"
    analysis_depth: Optional[str] = "comprehensive"


class CorrelationAnalysisRequest(BaseModel):
    correlation_matrix: Dict[str, Dict[str, float]]
    time_period: Optional[str] = "recent"


class RecommendationExplanationRequest(BaseModel):
    recommendations: Dict[str, Any]
    portfolio: Dict[str, float]
    market_conditions: Optional[str] = ""


class AnomalyAnalysisRequest(BaseModel):
    anomaly_data: Dict[str, Any]
    historical_context: Optional[str] = ""


class RegimeAnalysisRequest(BaseModel):
    regime_data: Dict[str, Any]
    transition_indicators: Dict[str, Any]


class ChatQueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = "default"
    include_context: Optional[bool] = True


class VectorSearchRequest(BaseModel):
    query_type: str  # 'text', 'symbol_pattern'
    query_data: Any
    k: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = {}


class PatternStorageRequest(BaseModel):
    pattern_id: str
    symbol: str
    pattern_type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}


@router.post("/analyze/market")
async def analyze_market(request: MarketAnalysisRequest):
    """
    Generate comprehensive market analysis using LLM.
    
    Args:
        request: Market analysis request
        
    Returns:
        AI-generated market analysis
    """
    try:
        logger.info(f"Generating market analysis for {len(request.symbols)} symbols")
        
        # Create task for LLM agent
        task_data = {
            'type': 'generate_market_analysis',
            'symbols': request.symbols,
            'time_period': request.time_period,
            'analysis_depth': request.analysis_depth
        }
        
        task = Task(
            id=f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="generate_market_analysis",
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        result = llm_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": f"Market analysis generated for {len(request.symbols)} symbols"
        }
        
    except Exception as e:
        logger.error(f"Market analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/correlations")
async def analyze_correlations(request: CorrelationAnalysisRequest):
    """
    Generate insights about correlation patterns.
    
    Args:
        request: Correlation analysis request
        
    Returns:
        Correlation insights
    """
    try:
        logger.info("Generating correlation insights")
        
        # Create task for LLM agent
        task_data = {
            'type': 'explain_correlations',
            'correlation_matrix': request.correlation_matrix,
            'time_period': request.time_period
        }
        
        task = Task(
            id=f"correlation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="explain_correlations",
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        result = llm_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": "Correlation analysis completed"
        }
        
    except Exception as e:
        logger.error(f"Correlation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain/recommendations")
async def explain_recommendations(request: RecommendationExplanationRequest):
    """
    Generate explanations for investment recommendations.
    
    Args:
        request: Recommendation explanation request
        
    Returns:
        Investment recommendation explanations
    """
    try:
        logger.info("Generating recommendation explanations")
        
        # Create task for LLM agent
        task_data = {
            'type': 'explain_recommendations',
            'recommendations': request.recommendations,
            'portfolio': request.portfolio,
            'market_conditions': request.market_conditions
        }
        
        task = Task(
            id=f"rec_explanation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="explain_recommendations",
            priority=TaskPriority.HIGH,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        result = llm_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": "Recommendation explanations generated"
        }
        
    except Exception as e:
        logger.error(f"Recommendation explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/anomaly")
async def analyze_anomaly(request: AnomalyAnalysisRequest):
    """
    Analyze market anomalies and provide insights.
    
    Args:
        request: Anomaly analysis request
        
    Returns:
        Anomaly analysis results
    """
    try:
        logger.info("Analyzing market anomaly")
        
        # Create task for LLM agent
        task_data = {
            'type': 'analyze_anomaly',
            'anomaly_data': request.anomaly_data,
            'historical_context': request.historical_context
        }
        
        task = Task(
            id=f"anomaly_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="analyze_anomaly",
            priority=TaskPriority.HIGH,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        result = llm_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": "Anomaly analysis completed"
        }
        
    except Exception as e:
        logger.error(f"Anomaly analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/regime")
async def analyze_regime_change(request: RegimeAnalysisRequest):
    """
    Analyze market regime changes.
    
    Args:
        request: Regime analysis request
        
    Returns:
        Regime change analysis
    """
    try:
        logger.info("Analyzing regime change")
        
        # Create task for LLM agent
        task_data = {
            'type': 'analyze_regime_change',
            'regime_data': request.regime_data,
            'transition_indicators': request.transition_indicators
        }
        
        task = Task(
            id=f"regime_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="analyze_regime_change",
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        result = llm_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": "Regime analysis completed"
        }
        
    except Exception as e:
        logger.error(f"Regime analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_query_flexible(data: Dict[str, Any] = Body(...)):
    """
    Process natural language queries about financial data (flexible endpoint).
    
    Args:
        data: Chat query data (flexible format)
        
    Returns:
        AI response to user query
    """
    try:
        query = data.get('message') or data.get('query', 'Hello')
        user_id = data.get('user_id', 'default')
        
        logger.info(f"Processing chat query: {query[:50]}...")
        
        # Mock response for now
        response = {
            "response": f"Thank you for your query: '{query}'. I'm currently in demo mode. "
                       f"This is a mock response showing the chat interface is working. "
                       f"To enable full AI capabilities, please ensure the Llama model is properly loaded.",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "model_status": "demo_mode",
            "context": "demo"
        }
        
        return {
            "status": "success",
            "data": response,
            "message": "Chat query processed (demo mode)"
        }
        
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        return {
            "status": "error", 
            "data": {"response": "Sorry, I encountered an error processing your request."},
            "message": str(e)
        }


@router.post("/vector/search")
async def vector_search_flexible(data: Dict[str, Any] = Body(...)):
    """
    Perform similarity search in vector database (flexible endpoint).
    
    Args:
        data: Vector search data (flexible format)
        
    Returns:
        Similar patterns from vector database
    """
    try:
        query = data.get('query_data', data.get('query', 'tech stocks'))
        query_type = data.get('query_type', 'text')
        k = data.get('k', 5)
        
        logger.info(f"Performing vector search: {query_type} for '{query}'")
        
        # Use actual vector database for search
        if query_type == 'text' or not query_type:
            # Text-based search using sentence embeddings
            results = vector_db.search_by_text_query(query, k=k)
        elif query_type == 'symbol_pattern':
            # Symbol pattern search (if price data is provided)
            symbol = data.get('symbol', 'AAPL')
            # For now, fallback to text search
            results = vector_db.search_by_text_query(f"{symbol} {query}", k=k)
        else:
            # Default to text search
            results = vector_db.search_by_text_query(query, k=k)
        
        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "pattern_id": result.get('pattern_id', ''),
                "symbol": result.get('symbol', ''),
                "similarity_score": result.get('similarity_score', 0.0),
                "pattern_type": result.get('pattern_type', ''),
                "description": f"Pattern: {result.get('pattern_id', '')} for {result.get('symbol', '')}",
                "metadata": result.get('metadata', {}),
                "timestamp": result.get('timestamp', ''),
                "distance": result.get('distance', 0.0)
            })
        
        return {
            "status": "success",
            "data": {
                "results": formatted_results,
                "count": len(formatted_results),
                "query": query,
                "query_type": query_type
            },
            "message": f"Found {len(formatted_results)} similar patterns in vector database"
        }
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return {
            "status": "error",
            "data": {"results": [], "count": 0},
            "message": str(e)
        }


@router.post("/vector/store")
async def store_pattern(request: PatternStorageRequest):
    """
    Store a financial pattern in the vector database.
    
    Args:
        request: Pattern storage request
        
    Returns:
        Storage confirmation
    """
    try:
        logger.info(f"Storing pattern: {request.pattern_id}")
        
        success = vector_db.add_financial_pattern(
            pattern_id=request.pattern_id,
            symbol=request.symbol,
            pattern_type=request.pattern_type,
            data=request.data,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to store pattern")
        
        return {
            "status": "success",
            "pattern_id": request.pattern_id,
            "message": "Pattern stored successfully"
        }
        
    except Exception as e:
        logger.error(f"Pattern storage failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector/stats")
async def get_vector_stats():
    """
    Get vector database statistics.
    
    Returns:
        Database statistics
    """
    try:
        stats = vector_db.get_pattern_statistics()
        
        return {
            "status": "success",
            "data": stats,
            "message": "Vector database statistics retrieved"
        }
        
    except Exception as e:
        logger.error(f"Failed to get vector stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_llm_status():
    """
    Get LLM engine and agent status.
    
    Returns:
        System status information
    """
    try:
        llm_info = llm_engine.get_model_info()
        agent_status = llm_agent.get_agent_status()
        vector_stats = vector_db.get_pattern_statistics()
        
        return {
            "status": "success",
            "data": {
                "llm_engine": llm_info,
                "llm_agent": agent_status,
                "vector_database": vector_stats
            },
            "message": "LLM system status retrieved"
        }
        
    except Exception as e:
        logger.error(f"Failed to get LLM status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights/generate")
async def generate_insights(
    trigger_type: str = Query("general", description="Type of insight trigger"),
    trigger_data: Dict[str, Any] = Body({})
):
    """
    Generate automated insights based on triggers.
    
    Args:
        trigger_type: Type of trigger (correlation_change, regime_change, etc.)
        trigger_data: Data associated with the trigger
        
    Returns:
        Generated insights
    """
    try:
        logger.info(f"Generating insights for trigger: {trigger_type}")
        
        # Create task for LLM agent
        task_data = {
            'type': 'generate_insights',
            'trigger_type': trigger_type,
            'trigger_data': trigger_data
        }
        
        task = Task(
            id=f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="generate_insights",
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        result = llm_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": f"Generated {result.get('count', 0)} insights"
        }
        
    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/available")
async def get_available_models():
    """
    Get information about available AI models.
    
    Returns:
        Available models information
    """
    try:
        models_info = {
            "llm_models": {
                "llama": {
                    "available": llm_engine.get_model_info()['model_available'],
                    "model_path": llm_engine.get_model_info()['model_path'],
                    "capabilities": [
                        "market_analysis",
                        "correlation_insights",
                        "recommendation_explanations",
                        "anomaly_analysis",
                        "regime_analysis",
                        "chat_interface"
                    ]
                }
            },
            "embedding_models": {
                "sentence_transformers": {
                    "model": "all-MiniLM-L6-v2",
                    "dimension": 384,
                    "capabilities": [
                        "text_embeddings",
                        "semantic_search",
                        "similarity_matching"
                    ]
                }
            },
            "vector_database": {
                "faiss": {
                    "index_type": vector_db.index_type,
                    "dimension": vector_db.dimension,
                    "total_patterns": vector_db.get_pattern_statistics()['total_patterns']
                }
            }
        }
        
        return {
            "status": "success",
            "data": models_info,
            "message": "Available models information retrieved"
        }
        
    except Exception as e:
        logger.error(f"Failed to get models info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vector/clear")
async def clear_vector_database():
    """
    Clear the vector database (use with caution).
    
    Returns:
        Confirmation of database clearing
    """
    try:
        vector_db.clear_index()
        
        return {
            "status": "success",
            "message": "Vector database cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear vector database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vector/save")
async def save_vector_index():
    """
    Save the vector database index to disk.
    
    Returns:
        Save confirmation
    """
    try:
        success = vector_db.save_index()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save vector index")
        
        return {
            "status": "success",
            "message": "Vector index saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to save vector index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vector/load")
async def load_vector_index():
    """
    Load the vector database index from disk.
    
    Returns:
        Load confirmation
    """
    try:
        success = vector_db.load_index()
        
        if not success:
            raise HTTPException(status_code=404, detail="No saved vector index found")
        
        return {
            "status": "success",
            "message": "Vector index loaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to load vector index: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 