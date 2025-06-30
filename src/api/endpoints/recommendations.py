"""
Recommendation API Endpoints
===========================

API endpoints for asset recommendations and portfolio optimization.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.recommendation_engine import AssetRecommendationEngine, PortfolioOptimizer
from src.agents.recommendation_agent import RecommendationAgent
from src.agents.base_agent import Task, TaskPriority

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Initialize components
recommendation_engine = AssetRecommendationEngine()
portfolio_optimizer = PortfolioOptimizer()
recommendation_agent = RecommendationAgent()


# Pydantic models for request/response
class PortfolioRequest(BaseModel):
    portfolio: Dict[str, float]
    universe: Optional[List[str]] = None
    strategy: Optional[str] = "balanced"
    horizon: Optional[str] = "1M"


class OptimizationRequest(BaseModel):
    portfolio: Dict[str, float]
    method: Optional[str] = "mean_variance"
    target_return: Optional[float] = None


class RiskAssessmentRequest(BaseModel):
    portfolio: Dict[str, float]
    risk_measures: Optional[List[str]] = ["var", "cvar", "max_drawdown"]


class RebalanceRequest(BaseModel):
    current_portfolio: Dict[str, float]
    target_portfolio: Dict[str, float]


@router.post("/generate")
async def generate_recommendations(request: PortfolioRequest):
    """
    Generate comprehensive asset recommendations.
    
    Args:
        request: Portfolio request with current holdings and parameters
        
    Returns:
        Comprehensive recommendation report with buy/sell signals
    """
    try:
        logger.info(f"Generating recommendations for portfolio with {len(request.portfolio)} assets")
        
        # Set default universe if not provided
        universe = request.universe or [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 
            'JPM', 'JNJ', 'V', 'WMT', 'PG', 'HD', 'MA', 'UNH'
        ]
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            portfolio=request.portfolio,
            universe=universe,
            horizon=request.horizon,
            strategy=request.strategy
        )
        
        if 'error' in recommendations:
            raise HTTPException(status_code=400, detail=recommendations['error'])
        
        return {
            "status": "success",
            "data": recommendations,
            "message": f"Generated recommendations for {len(universe)} assets"
        }
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_portfolio(request: OptimizationRequest):
    """
    Optimize portfolio allocation using various methods.
    
    Args:
        request: Optimization request with portfolio and method
        
    Returns:
        Optimal portfolio weights and metrics
    """
    try:
        logger.info(f"Optimizing portfolio using {request.method}")
        
        # Create task for recommendation agent
        task_data = {
            'type': 'optimize_portfolio',
            'portfolio': request.portfolio,
            'method': request.method,
            'target_return': request.target_return
        }
        
        task = Task(
            id=f"optimize_{len(request.portfolio)}_{request.method}",
            name="optimize_portfolio",
            priority=TaskPriority.HIGH,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        # Process task
        result = recommendation_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": f"Portfolio optimized using {request.method}"
        }
        
    except Exception as e:
        logger.error(f"Portfolio optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_portfolio(request: PortfolioRequest):
    """
    Analyze portfolio performance and characteristics.
    
    Args:
        request: Portfolio request with holdings
        
    Returns:
        Comprehensive portfolio analysis
    """
    try:
        logger.info(f"Analyzing portfolio with {len(request.portfolio)} assets")
        
        # Create task for recommendation agent
        task_data = {
            'type': 'analyze_portfolio',
            'portfolio': request.portfolio,
            'benchmark': 'SPY'
        }
        
        task = Task(
            id=f"analyze_{len(request.portfolio)}",
            name="analyze_portfolio",
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        # Process task
        result = recommendation_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": f"Portfolio analysis completed for {len(request.portfolio)} assets"
        }
        
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-assessment")
async def assess_portfolio_risk(request: RiskAssessmentRequest):
    """
    Assess portfolio risk using various risk measures.
    
    Args:
        request: Risk assessment request with portfolio and measures
        
    Returns:
        Comprehensive risk assessment
    """
    try:
        logger.info(f"Assessing risk for portfolio with {len(request.portfolio)} assets")
        
        # Create task for recommendation agent
        task_data = {
            'type': 'risk_assessment',
            'portfolio': request.portfolio,
            'risk_measures': request.risk_measures
        }
        
        task = Task(
            id=f"risk_{len(request.portfolio)}",
            name="risk_assessment",
            priority=TaskPriority.HIGH,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        # Process task
        result = recommendation_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": f"Risk assessment completed for {len(request.portfolio)} assets"
        }
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebalance-check")
async def check_rebalancing(request: RebalanceRequest):
    """
    Check if portfolio needs rebalancing.
    
    Args:
        request: Rebalance request with current and target portfolios
        
    Returns:
        Rebalancing analysis and recommendations
    """
    try:
        logger.info("Checking rebalancing requirements")
        
        # Create task for recommendation agent
        task_data = {
            'type': 'rebalance_check',
            'current_portfolio': request.current_portfolio,
            'target_portfolio': request.target_portfolio
        }
        
        task = Task(
            id="rebalance_check",
            name="rebalance_check",
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        # Process task
        result = recommendation_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": "Rebalancing analysis completed"
        }
        
    except Exception as e:
        logger.error(f"Rebalancing check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_available_strategies():
    """
    Get available investment strategies.
    
    Returns:
        List of available strategies with descriptions
    """
    strategies = {
        "conservative": {
            "description": "Low-risk, stable returns with focus on capital preservation",
            "characteristics": ["Low volatility", "High diversification", "Defensive assets"],
            "risk_level": "Low"
        },
        "balanced": {
            "description": "Balanced approach between growth and stability",
            "characteristics": ["Moderate risk", "Diversified allocation", "Growth and value mix"],
            "risk_level": "Medium"
        },
        "aggressive": {
            "description": "High-growth potential with higher risk tolerance",
            "characteristics": ["High growth potential", "Higher volatility", "Growth-focused"],
            "risk_level": "High"
        },
        "diversified": {
            "description": "Maximum diversification across asset classes",
            "characteristics": ["Low correlation", "Broad diversification", "Risk reduction"],
            "risk_level": "Low-Medium"
        }
    }
    
    return {
        "status": "success",
        "data": strategies,
        "message": "Available investment strategies"
    }


@router.get("/universe")
async def get_default_universe():
    """
    Get default asset universe for recommendations.
    
    Returns:
        Default list of assets available for recommendations
    """
    universe = {
        "large_cap_tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
        "financials": ["JPM", "BAC", "WFC", "GS", "MS", "V", "MA"],
        "healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT"],
        "consumer": ["WMT", "PG", "KO", "PEP", "MCD", "NKE"],
        "industrials": ["BA", "CAT", "GE", "HON", "UPS", "LMT"],
        "energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
        "etfs": ["SPY", "QQQ", "IWM", "GLD", "TLT", "VTI"]
    }
    
    # Flatten to single list
    all_symbols = []
    for category, symbols in universe.items():
        all_symbols.extend(symbols)
    
    return {
        "status": "success",
        "data": {
            "all_symbols": list(set(all_symbols)),
            "by_category": universe,
            "total_count": len(set(all_symbols))
        },
        "message": "Default asset universe"
    }


@router.get("/agent-status")
async def get_agent_status():
    """
    Get recommendation agent status.
    
    Returns:
        Current status of the recommendation agent
    """
    try:
        status = recommendation_agent.get_agent_status()
        
        return {
            "status": "success",
            "data": status,
            "message": "Recommendation agent status"
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-recommendation")
async def quick_recommendation(
    symbols: List[str] = Query(..., description="List of symbols to analyze"),
    strategy: str = Query("balanced", description="Investment strategy"),
    current_cash: float = Query(10000.0, description="Available cash for investment")
):
    """
    Generate quick recommendations for new investments.
    
    Args:
        symbols: List of symbols to consider
        strategy: Investment strategy
        current_cash: Available cash amount
        
    Returns:
        Quick investment recommendations
    """
    try:
        logger.info(f"Generating quick recommendations for {len(symbols)} symbols")
        
        # Generate recommendations with empty portfolio (new investment)
        recommendations = recommendation_engine.generate_recommendations(
            portfolio={},  # Empty portfolio for new investment
            universe=symbols,
            horizon="1M",
            strategy=strategy
        )
        
        if 'error' in recommendations:
            raise HTTPException(status_code=400, detail=recommendations['error'])
        
        # Calculate position sizes based on available cash
        optimal_weights = recommendations.get('optimal_weights', {})
        position_sizes = {}
        
        for symbol, weight in optimal_weights.items():
            position_sizes[symbol] = {
                'weight': weight,
                'dollar_amount': current_cash * weight,
                'recommended_action': 'buy'
            }
        
        quick_rec = {
            'investment_amount': current_cash,
            'strategy': strategy,
            'position_sizes': position_sizes,
            'risk_level': recommendations.get('risk_assessment', {}).get('overall_risk_level', 'medium'),
            'summary': recommendations.get('summary', ''),
            'buy_signals': recommendations.get('buy_signals', [])
        }
        
        return {
            "status": "success",
            "data": quick_rec,
            "message": f"Quick recommendations generated for ${current_cash:,.2f} investment"
        }
        
    except Exception as e:
        logger.error(f"Quick recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-metrics")
async def get_performance_metrics(
    portfolio_id: str = Query("default", description="Portfolio ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get recommendation performance metrics.
    
    Args:
        portfolio_id: Portfolio identifier
        start_date: Analysis start date
        end_date: Analysis end date
        
    Returns:
        Performance metrics and analysis
    """
    try:
        logger.info(f"Getting performance metrics for portfolio: {portfolio_id}")
        
        # Create task for recommendation agent
        task_data = {
            'type': 'performance_analysis',
            'portfolio_id': portfolio_id,
            'start_date': start_date,
            'end_date': end_date
        }
        
        task = Task(
            id=f"performance_{portfolio_id}",
            name="performance_analysis",
            priority=TaskPriority.LOW,
            created_at=datetime.now(),
            scheduled_at=None,
            data=task_data
        )
        
        # Process task
        result = recommendation_agent._handle_task(task)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "status": "success",
            "data": result,
            "message": f"Performance metrics for portfolio {portfolio_id}"
        }
        
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))