#!/usr/bin/env python3
"""
Mock API Server for Frontend Development
Provides basic endpoints while main API is being fixed
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json
import random
from datetime import datetime, timedelta

app = FastAPI(title="Mock Multi-Market Correlation API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint."""
    return {"status": "healthy", "api_version": "mock-1.0.0"}

@app.get("/llm/status")
async def llm_status():
    """LLM status endpoint."""
    return {
        "status": "operational",
        "model_available": True,
        "model_name": "llama-2-7b-chat",
        "model_path": "data/models/llama-2-7b-chat.Q4_0.gguf",
        "llama_available": True,
        "capabilities": ["chat", "analysis", "recommendations"]
    }

@app.post("/llm/chat")
async def chat_endpoint(data: Dict[str, Any]):
    """Mock chat endpoint."""
    message = data.get("message", "")
    
    # Generate contextual responses based on message content
    responses = {
        "correlation": "Based on current market data, I observe strong positive correlations between tech stocks (AAPL, GOOGL, MSFT) at 0.85, while crypto shows inverse correlation with traditional assets at -0.23. The S&P 500 correlation matrix indicates sector rotation patterns.",
        "diversification": "For optimal portfolio diversification, I recommend a mix of 40% equities (distributed across sectors), 20% bonds, 15% REITs, 15% commodities, and 10% crypto. This allocation targets a Sharpe ratio of 1.2+ while maintaining correlation coefficients below 0.6.",
        "risk": "Current market volatility analysis shows VIX at elevated levels. I recommend implementing a risk-parity approach with dynamic hedging using options strategies. Beta-adjusted exposure should be maintained at 0.8 during high uncertainty periods.",
        "market": "Today's market analysis reveals: SPY up 1.2%, tech sector leading with QQQ +2.1%. Notable divergence in small-caps (IWM -0.3%). Bond yields stable at 4.2%. Crypto market showing resilience with BTC +3.5%.",
        "trading": "I'm seeing several promising trading opportunities: AAPL showing strong momentum with bullish RSI divergence, BTC breaking above resistance at $43,500, and defensive sectors showing rotation potential. Consider position sizing at 2-3% per trade.",
        "portfolio": "Your current portfolio allocation shows 65% equities, 25% bonds, 10% alternatives. I recommend rebalancing to reduce tech exposure from 40% to 30% and increasing international diversification. The correlation matrix suggests adding commodities for hedge.",
        "default": "I'm analyzing current market correlations and can provide insights on portfolio optimization, risk management, and asset allocation strategies. What specific aspect of market analysis would you like me to focus on?"
    }
    
    # Determine response type based on message content
    response_key = "default"
    for key in responses.keys():
        if key in message.lower():
            response_key = key
            break
    
    return {
        "success": True,
        "data": {
            "response": responses[response_key],
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.92,
            "sources": ["market_data", "correlation_analysis", "risk_models"]
        }
    }

@app.get("/api/correlations")
async def get_correlations():
    """Mock correlations endpoint."""
    # Generate realistic correlation data
    assets = ["AAPL", "GOOGL", "MSFT", "TSLA", "SPY", "QQQ", "BTC", "ETH"]
    correlations = {}
    
    for i, asset1 in enumerate(assets):
        correlations[asset1] = {}
        for j, asset2 in enumerate(assets):
            if i == j:
                correlations[asset1][asset2] = 1.0
            else:
                # Generate realistic correlations
                if "BTC" in [asset1, asset2] or "ETH" in [asset1, asset2]:
                    corr = random.uniform(-0.2, 0.4)  # Crypto correlations
                elif asset1 in ["AAPL", "GOOGL", "MSFT"] and asset2 in ["AAPL", "GOOGL", "MSFT"]:
                    corr = random.uniform(0.7, 0.9)  # Tech stocks
                else:
                    corr = random.uniform(0.3, 0.8)  # General market
                
                correlations[asset1][asset2] = round(corr, 3)
    
    return {
        "correlations": correlations,
        "timestamp": datetime.now().isoformat(),
        "period": "1Y"
    }

@app.get("/api/recommendations")
async def get_recommendations():
    """Mock recommendations endpoint."""
    recommendations = [
        {
            "type": "BUY",
            "asset": "AAPL",
            "confidence": 0.87,
            "reason": "Strong correlation with tech sector momentum, earnings upside potential",
            "target_price": 195.50,
            "risk_level": "Medium"
        },
        {
            "type": "HOLD",
            "asset": "BTC",
            "confidence": 0.72,
            "reason": "Low correlation with traditional assets provides diversification benefits",
            "target_price": 45000,
            "risk_level": "High"
        },
        {
            "type": "REDUCE",
            "asset": "TSLA",
            "confidence": 0.65,
            "reason": "High volatility and correlation with speculative assets",
            "target_price": 180.00,
            "risk_level": "High"
        }
    ]
    
    return {
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(),
        "model_version": "correlation-v1.2"
    }

@app.get("/api/agents/status")
async def get_agents_status():
    """Mock agents status endpoint."""
    return {
        "agents": {
            "data_collection": {"status": "active", "last_run": datetime.now().isoformat()},
            "analysis": {"status": "active", "last_run": datetime.now().isoformat()},
            "llm": {"status": "active", "last_run": datetime.now().isoformat()},
            "recommendation": {"status": "active", "last_run": datetime.now().isoformat()},
            "reporting": {"status": "idle", "last_run": (datetime.now() - timedelta(hours=1)).isoformat()}
        },
        "system_health": "optimal"
    }

@app.post("/llm/vector/search")
async def vector_search_endpoint(data: Dict[str, Any]):
    """Mock vector search endpoint."""
    query = data.get("query_data", "")
    k = data.get("k", 5)
    
    # Generate mock vector search results
    mock_results = [
        {
            "score": 0.95,
            "content": f"AAPL showing strong correlation with tech sector momentum, up 2.3% in pre-market trading",
            "metadata": {"symbol": "AAPL", "sector": "Technology", "correlation": 0.87}
        },
        {
            "score": 0.89,
            "content": f"High volatility detected in TSLA with 15% price swing over 5 days",
            "metadata": {"symbol": "TSLA", "sector": "Automotive", "volatility": 0.35}
        },
        {
            "score": 0.82,
            "content": f"BTC breaking resistance levels, showing inverse correlation with traditional assets",
            "metadata": {"symbol": "BTC", "asset_class": "Crypto", "correlation": -0.15}
        },
        {
            "score": 0.78,
            "content": f"Tech sector rotation pattern identified with QQQ outperforming SPY by 1.8%",
            "metadata": {"sector": "Technology", "relative_strength": 1.8}
        },
        {
            "score": 0.71,
            "content": f"Energy sector showing defensive characteristics amid market uncertainty",
            "metadata": {"sector": "Energy", "beta": 0.65}
        }
    ]
    
    # Filter results based on query
    filtered_results = mock_results[:k]
    
    return {
        "success": True,
        "data": {
            "results": filtered_results,
            "count": len(filtered_results),
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
    }

@app.get("/llm/vector/stats")
async def vector_stats_endpoint():
    """Mock vector database stats endpoint."""
    return {
        "success": True,
        "data": {
            "total_patterns": 15847,
            "indexed_documents": 3421,
            "last_updated": datetime.now().isoformat(),
            "index_size": "2.3GB",
            "search_latency_ms": 45
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mock API Server...")
    print("📊 Endpoints available:")
    print("   - Health: http://localhost:8000/health")
    print("   - LLM Status: http://localhost:8000/llm/status")
    print("   - Chat: http://localhost:8000/llm/chat")
    print("   - Correlations: http://localhost:8000/api/correlations")
    print("   - Recommendations: http://localhost:8000/api/recommendations")
    print("   - Vector Search: http://localhost:8000/llm/vector/search")
    print("   - Vector Stats: http://localhost:8000/llm/vector/stats")
    uvicorn.run(app, host="0.0.0.0", port=8000) 