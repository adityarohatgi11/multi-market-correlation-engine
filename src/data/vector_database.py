"""
FAISS Vector Database Manager
============================

Advanced vector database implementation for financial data similarity search.
Supports embedding generation, vector indexing, and semantic search capabilities.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

import os
import pickle
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from ..config.config_manager import get_config

logger = logging.getLogger(__name__)


class FinancialEmbedding:
    """
    Generate embeddings for financial data patterns.
    """
    
    def __init__(self):
        """Initialize the financial embedding generator."""
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=384)  # Match sentence transformer dimensions
        self.is_fitted = False
        
    def create_price_pattern_embedding(self, price_data: pd.Series, window: int = 30) -> np.ndarray:
        """
        Create embeddings from price patterns.
        
        Args:
            price_data: Time series of prices
            window: Window size for pattern extraction
            
        Returns:
            Embedding vector
        """
        try:
            # Calculate technical indicators
            returns = price_data.pct_change().dropna()
            
            # Feature extraction
            features = []
            
            # Statistical features
            features.extend([
                returns.mean(),
                returns.std(),
                returns.skew(),
                returns.kurtosis(),
                returns.min(),
                returns.max()
            ])
            
            # Rolling statistics
            for w in [5, 10, 20]:
                if len(returns) >= w:
                    rolling_mean = returns.rolling(w).mean().iloc[-1]
                    rolling_std = returns.rolling(w).std().iloc[-1]
                    features.extend([rolling_mean, rolling_std])
                else:
                    features.extend([0.0, 0.0])
            
            # Price momentum features
            if len(price_data) >= 20:
                momentum_5 = (price_data.iloc[-1] / price_data.iloc[-6]) - 1
                momentum_10 = (price_data.iloc[-1] / price_data.iloc[-11]) - 1
                momentum_20 = (price_data.iloc[-1] / price_data.iloc[-21]) - 1
                features.extend([momentum_5, momentum_10, momentum_20])
            else:
                features.extend([0.0, 0.0, 0.0])
            
            # Volatility patterns
            if len(returns) >= 10:
                volatility = returns.rolling(10).std().iloc[-1]
                avg_volatility = returns.rolling(10).std().mean()
                vol_ratio = volatility / avg_volatility if avg_volatility > 0 else 1.0
                features.extend([volatility, vol_ratio])
            else:
                features.extend([0.0, 1.0])
            
            # Pad or truncate to fixed size
            target_size = 20
            if len(features) < target_size:
                features.extend([0.0] * (target_size - len(features)))
            else:
                features = features[:target_size]
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error creating price pattern embedding: {e}")
            return np.zeros(20, dtype=np.float32)
    
    def create_correlation_embedding(self, correlation_matrix: pd.DataFrame) -> np.ndarray:
        """
        Create embeddings from correlation matrices.
        
        Args:
            correlation_matrix: Correlation matrix
            
        Returns:
            Embedding vector
        """
        try:
            # Flatten upper triangle of correlation matrix
            n = correlation_matrix.shape[0]
            triu_indices = np.triu_indices(n, k=1)
            correlations = correlation_matrix.values[triu_indices]
            
            # Statistical features of correlations
            features = [
                correlations.mean(),
                correlations.std(),
                correlations.min(),
                correlations.max(),
                np.median(correlations),
                len(correlations[correlations > 0.5]),  # Strong positive correlations
                len(correlations[correlations < -0.5]),  # Strong negative correlations
                len(correlations[abs(correlations) < 0.1])  # Weak correlations
            ]
            
            # Add top correlations (padded/truncated to fixed size)
            sorted_corrs = np.sort(correlations)[::-1]
            top_corrs = sorted_corrs[:10]
            if len(top_corrs) < 10:
                top_corrs = np.pad(top_corrs, (0, 10 - len(top_corrs)), 'constant')
            
            features.extend(top_corrs.tolist())
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error creating correlation embedding: {e}")
            return np.zeros(18, dtype=np.float32)
    
    def create_regime_embedding(self, regime_data: Dict[str, Any]) -> np.ndarray:
        """
        Create embeddings from market regime data.
        
        Args:
            regime_data: Dictionary containing regime information
            
        Returns:
            Embedding vector
        """
        try:
            features = []
            
            # Regime probabilities
            for regime in ['bull', 'bear', 'neutral', 'crisis', 'recovery']:
                prob = regime_data.get(f'{regime}_probability', 0.0)
                features.append(prob)
            
            # Market characteristics
            features.extend([
                regime_data.get('volatility_level', 0.0),
                regime_data.get('correlation_level', 0.0),
                regime_data.get('market_stress_index', 0.0),
                regime_data.get('vix_level', 0.0),
                regime_data.get('yield_curve_slope', 0.0)
            ])
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error creating regime embedding: {e}")
            return np.zeros(10, dtype=np.float32)
    
    def create_text_embedding(self, text: str) -> np.ndarray:
        """
        Create embeddings from text using sentence transformers.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.sentence_model.encode(text)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error creating text embedding: {e}")
            return np.zeros(384, dtype=np.float32)
    
    def create_composite_embedding(self, 
                                 price_data: Optional[pd.Series] = None,
                                 correlation_data: Optional[pd.DataFrame] = None,
                                 regime_data: Optional[Dict] = None,
                                 text_data: Optional[str] = None) -> np.ndarray:
        """
        Create composite embedding combining multiple data types.
        
        Args:
            price_data: Price time series
            correlation_data: Correlation matrix
            regime_data: Market regime information
            text_data: Textual description
            
        Returns:
            Composite embedding vector
        """
        embeddings = []
        
        if price_data is not None:
            price_emb = self.create_price_pattern_embedding(price_data)
            embeddings.append(price_emb)
        
        if correlation_data is not None:
            corr_emb = self.create_correlation_embedding(correlation_data)
            embeddings.append(corr_emb)
        
        if regime_data is not None:
            regime_emb = self.create_regime_embedding(regime_data)
            embeddings.append(regime_emb)
        
        if text_data is not None:
            text_emb = self.create_text_embedding(text_data)
            embeddings.append(text_emb)
        
        if not embeddings:
            return np.zeros(384, dtype=np.float32)
        
        # Concatenate all embeddings
        composite = np.concatenate(embeddings)
        
        # Normalize to fixed dimension using PCA if needed
        if not self.is_fitted and len(composite) > 384:
            # For first time, fit PCA
            composite_reshaped = composite.reshape(1, -1)
            self.pca.fit(composite_reshaped)
            self.is_fitted = True
            result = self.pca.transform(composite_reshaped)[0]
        elif len(composite) > 384:
            # Use fitted PCA
            composite_reshaped = composite.reshape(1, -1)
            result = self.pca.transform(composite_reshaped)[0]
        else:
            # Pad if too small
            result = np.pad(composite, (0, max(0, 384 - len(composite))), 'constant')
        
        return result.astype(np.float32)


class FAISSVectorDatabase:
    """
    FAISS-based vector database for financial data similarity search.
    """
    
    def __init__(self, dimension: int = 384, index_type: str = "IVF"):
        """
        Initialize FAISS vector database.
        
        Args:
            dimension: Embedding dimension
            index_type: FAISS index type (Flat, IVF, HNSW)
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.metadata = []
        self.embedding_generator = FinancialEmbedding()
        
        # Create FAISS index
        self._create_index()
        
        # Storage paths
        config = get_config()
        self.data_dir = "data/vectors"
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"FAISS Vector Database initialized with {index_type} index, dimension: {dimension}")
    
    def _create_index(self):
        """Create FAISS index based on specified type."""
        if self.index_type == "Flat":
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "IVF":
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        elif self.index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        logger.info(f"Created FAISS {self.index_type} index")
    
    def add_financial_pattern(self, 
                            pattern_id: str,
                            symbol: str,
                            pattern_type: str,
                            data: Dict[str, Any],
                            metadata: Optional[Dict] = None) -> bool:
        """
        Add financial pattern to the vector database.
        
        Args:
            pattern_id: Unique identifier for the pattern
            symbol: Financial symbol
            pattern_type: Type of pattern (price, correlation, regime, etc.)
            data: Pattern data
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Generate embedding based on pattern type
            if pattern_type == "price_pattern":
                embedding = self.embedding_generator.create_price_pattern_embedding(
                    data.get('price_series')
                )
            elif pattern_type == "correlation_pattern":
                embedding = self.embedding_generator.create_correlation_embedding(
                    data.get('correlation_matrix')
                )
            elif pattern_type == "regime_pattern":
                embedding = self.embedding_generator.create_regime_embedding(
                    data.get('regime_data')
                )
            elif pattern_type == "composite_pattern":
                embedding = self.embedding_generator.create_composite_embedding(
                    price_data=data.get('price_data'),
                    correlation_data=data.get('correlation_data'),
                    regime_data=data.get('regime_data'),
                    text_data=data.get('text_data')
                )
            else:
                logger.error(f"Unknown pattern type: {pattern_type}")
                return False
            
            # Ensure correct dimension
            if len(embedding) != self.dimension:
                # Pad or truncate
                if len(embedding) < self.dimension:
                    embedding = np.pad(embedding, (0, self.dimension - len(embedding)), 'constant')
                else:
                    embedding = embedding[:self.dimension]
            
            # Add to FAISS index
            embedding_2d = embedding.reshape(1, -1)
            
            # Train index if needed (for IVF)
            if self.index_type == "IVF" and not self.index.is_trained:
                if len(self.metadata) >= 100:  # Need enough data to train
                    all_embeddings = np.array([self._get_embedding_by_id(mid['pattern_id']) 
                                             for mid in self.metadata if mid is not None])
                    if len(all_embeddings) > 0:
                        self.index.train(all_embeddings)
            
            if self.index_type != "IVF" or self.index.is_trained:
                self.index.add(embedding_2d)
                
                # Store metadata
                pattern_metadata = {
                    'pattern_id': pattern_id,
                    'symbol': symbol,
                    'pattern_type': pattern_type,
                    'timestamp': datetime.now().isoformat(),
                    'embedding': embedding,
                    'metadata': metadata or {}
                }
                self.metadata.append(pattern_metadata)
                
                logger.info(f"Added pattern {pattern_id} ({pattern_type}) for {symbol}")
                return True
            else:
                logger.warning(f"Index not trained yet, need more data")
                return False
                
        except Exception as e:
            logger.error(f"Error adding financial pattern: {e}")
            return False
    
    def search_similar_patterns(self, 
                              query_embedding: np.ndarray,
                              k: int = 5,
                              pattern_type: Optional[str] = None,
                              symbol_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar patterns in the vector database.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            pattern_type: Filter by pattern type
            symbol_filter: Filter by symbols
            
        Returns:
            List of similar patterns with scores
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector database is empty")
                return []
            
            # Ensure correct dimension
            if len(query_embedding) != self.dimension:
                if len(query_embedding) < self.dimension:
                    query_embedding = np.pad(query_embedding, (0, self.dimension - len(query_embedding)), 'constant')
                else:
                    query_embedding = query_embedding[:self.dimension]
            
            # Search in FAISS index
            query_2d = query_embedding.reshape(1, -1)
            distances, indices = self.index.search(query_2d, min(k * 2, self.index.ntotal))
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue
                    
                if idx >= len(self.metadata):
                    continue
                
                metadata = self.metadata[idx]
                if metadata is None:
                    continue
                
                # Apply filters
                if pattern_type and metadata.get('pattern_type') != pattern_type:
                    continue
                
                if symbol_filter and metadata.get('symbol') not in symbol_filter:
                    continue
                
                result = {
                    'pattern_id': metadata['pattern_id'],
                    'symbol': metadata['symbol'],
                    'pattern_type': metadata['pattern_type'],
                    'similarity_score': float(1.0 / (1.0 + distance)),  # Convert distance to similarity
                    'distance': float(distance),
                    'timestamp': metadata['timestamp'],
                    'metadata': metadata['metadata']
                }
                results.append(result)
                
                if len(results) >= k:
                    break
            
            logger.info(f"Found {len(results)} similar patterns")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar patterns: {e}")
            return []
    
    def search_by_symbol_pattern(self, 
                               symbol: str,
                               price_data: pd.Series,
                               k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for patterns similar to a symbol's price pattern.
        
        Args:
            symbol: Symbol identifier
            price_data: Price time series
            k: Number of results
            
        Returns:
            Similar patterns
        """
        embedding = self.embedding_generator.create_price_pattern_embedding(price_data)
        return self.search_similar_patterns(embedding, k, pattern_type="price_pattern")
    
    def search_by_text_query(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search patterns using natural language query.
        
        Args:
            query: Natural language query
            k: Number of results
            
        Returns:
            Relevant patterns
        """
        embedding = self.embedding_generator.create_text_embedding(query)
        return self.search_similar_patterns(embedding, k)
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored patterns.
        
        Returns:
            Statistics dictionary
        """
        if not self.metadata:
            return {'total_patterns': 0}
        
        pattern_types = {}
        symbols = set()
        
        for meta in self.metadata:
            if meta is None:
                continue
                
            pattern_type = meta.get('pattern_type', 'unknown')
            pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1
            symbols.add(meta.get('symbol', 'unknown'))
        
        return {
            'total_patterns': len(self.metadata),
            'pattern_types': pattern_types,
            'unique_symbols': len(symbols),
            'symbols': list(symbols),
            'index_type': self.index_type,
            'dimension': self.dimension,
            'is_trained': getattr(self.index, 'is_trained', True)
        }
    
    def save_index(self, filepath: Optional[str] = None) -> bool:
        """
        Save FAISS index and metadata to disk.
        
        Args:
            filepath: Custom file path
            
        Returns:
            Success status
        """
        try:
            if filepath is None:
                filepath = os.path.join(self.data_dir, f"faiss_index_{self.index_type.lower()}")
            
            # Save FAISS index
            faiss.write_index(self.index, f"{filepath}.index")
            
            # Save metadata
            with open(f"{filepath}.metadata", 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Saved FAISS index to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            return False
    
    def load_index(self, filepath: Optional[str] = None) -> bool:
        """
        Load FAISS index and metadata from disk.
        
        Args:
            filepath: Custom file path
            
        Returns:
            Success status
        """
        try:
            if filepath is None:
                filepath = os.path.join(self.data_dir, f"faiss_index_{self.index_type.lower()}")
            
            # Load FAISS index
            if os.path.exists(f"{filepath}.index"):
                self.index = faiss.read_index(f"{filepath}.index")
                
                # Load metadata
                if os.path.exists(f"{filepath}.metadata"):
                    with open(f"{filepath}.metadata", 'rb') as f:
                        self.metadata = pickle.load(f)
                
                logger.info(f"Loaded FAISS index from {filepath}")
                return True
            else:
                logger.warning(f"Index file not found: {filepath}.index")
                return False
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            return False
    
    def _get_embedding_by_id(self, pattern_id: str) -> Optional[np.ndarray]:
        """Get embedding by pattern ID."""
        for meta in self.metadata:
            if meta and meta.get('pattern_id') == pattern_id:
                return meta.get('embedding')
        return None
    
    def clear_index(self):
        """Clear the vector database."""
        self._create_index()
        self.metadata = []
        logger.info("Cleared FAISS vector database")


# Global vector database instance
_vector_db = None


def get_vector_db() -> FAISSVectorDatabase:
    """
    Get the global vector database instance.
    
    Returns:
        FAISSVectorDatabase instance
    """
    global _vector_db
    if _vector_db is None:
        _vector_db = FAISSVectorDatabase(index_type="Flat")
        # Try to load existing Flat index
        _vector_db.load_index("data/vectors/faiss_index_flat")
    return _vector_db


if __name__ == "__main__":
    # Test vector database functionality
    try:
        db = get_vector_db()
        print("✅ FAISS Vector Database initialized successfully!")
        
        # Test with sample data
        sample_prices = pd.Series([100, 101, 99, 102, 98, 103, 97], 
                                 index=pd.date_range('2024-01-01', periods=7))
        
        success = db.add_financial_pattern(
            pattern_id="test_pattern_001",
            symbol="TEST",
            pattern_type="price_pattern",
            data={'price_series': sample_prices}
        )
        
        if success:
            print("✅ Added test pattern successfully!")
            
            # Test search
            results = db.search_by_symbol_pattern("TEST", sample_prices, k=1)
            print(f"✅ Search returned {len(results)} results")
            
            # Print statistics
            stats = db.get_pattern_statistics()
            print(f"📊 Database stats: {stats}")
        
    except Exception as e:
        print(f"❌ Vector database test failed: {e}") 