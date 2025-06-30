// API Response Types
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp?: string
}

// Market Data Types
export interface MarketData {
  symbol: string
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  adj_close?: number
}

export interface CorrelationMatrix {
  [symbol: string]: {
    [symbol: string]: number
  }
}

export interface Portfolio {
  [symbol: string]: number // symbol -> weight
}

// Recommendation Types
export interface Recommendation {
  id: string
  symbol: string
  action: 'buy' | 'sell' | 'hold'
  confidence: number
  reasoning: string
  target_price?: number
  stop_loss?: number
  expected_return?: number
  risk_level: 'low' | 'medium' | 'high'
  timestamp: string
}

export interface RecommendationRequest {
  portfolio: Portfolio
  strategy: 'conservative' | 'balanced' | 'aggressive'
  time_horizon: '1M' | '3M' | '6M' | '1Y'
  risk_tolerance: 'low' | 'medium' | 'high'
  symbols?: string[]
}

// Vector Database Types
export interface VectorPattern {
  pattern_id: string
  symbol: string
  pattern_type: string
  similarity_score?: number
  distance?: number
  timestamp: string
  metadata: Record<string, any>
}

export interface VectorSearchRequest {
  query: string
  k?: number
  pattern_type?: string
  symbol_filter?: string[]
}

export interface VectorStoreRequest {
  pattern_id: string
  symbol: string
  pattern_type: string
  data: Record<string, any>
  metadata?: Record<string, any>
}

export interface VectorStats {
  total_patterns: number
  pattern_types: Record<string, number>
  unique_symbols: number
  symbols: string[]
  index_type: string
  dimension: number
  is_trained: boolean
}

// LLM Types
export interface LLMStatus {
  model_available: boolean
  model_path?: string
  llama_available: boolean
  vector_patterns: number
  system_status: 'ready' | 'loading' | 'error'
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface ChatRequest {
  message: string
  context?: Record<string, any>
  conversation_id?: string
}

export interface MarketAnalysisRequest {
  symbols: string[]
  time_period?: string
  context?: string
}

export interface MarketAnalysis {
  analysis: string
  insights: string[]
  risk_assessment: string
  recommendations: string[]
  confidence: number
  timestamp: string
}

// ML Model Types
export interface MLPrediction {
  symbol: string
  predicted_price: number
  confidence: number
  model_type: string
  timestamp: string
}

export interface RegimeAnalysis {
  current_regime: string
  regime_probabilities: Record<string, number>
  transition_probability: number
  characteristics: string[]
  timestamp: string
}

// Chart Data Types
export interface ChartDataPoint {
  x: string | number
  y: number
  label?: string
  color?: string
}

export interface TimeSeriesPoint {
  date: string
  value: number
  symbol?: string
}

// UI State Types
export interface DashboardTab {
  id: string
  label: string
  icon: React.ComponentType<any>
  component: React.ComponentType<any>
  badge?: number
}

export interface NotificationState {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
}

// Form Types
export interface SymbolSelectionForm {
  symbols: string[]
  timeRange: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y'
  includeVolume: boolean
}

export interface PortfolioForm {
  allocations: Record<string, number>
  totalValue: number
  rebalance: boolean
}

// Error Types
export interface ApiError {
  message: string
  code?: string
  details?: Record<string, any>
  timestamp: string
}

// Component Props Types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface LoadingProps extends BaseComponentProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

export interface CardProps extends BaseComponentProps {
  title?: string
  subtitle?: string
  action?: React.ReactNode
  loading?: boolean
}

// State Management Types
export interface AppState {
  user: {
    preferences: {
      theme: 'light' | 'dark'
      currency: 'USD' | 'EUR' | 'GBP'
      timezone: string
    }
  }
  market: {
    selectedSymbols: string[]
    timeRange: string
    lastUpdate: string
  }
  llm: {
    chatHistory: ChatMessage[]
    isConnected: boolean
    modelStatus: LLMStatus
  }
  notifications: NotificationState[]
}

// Utility Types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>

// API Client Types
export interface ApiClientConfig {
  baseURL: string
  timeout?: number
  headers?: Record<string, string>
}

export interface QueryParams {
  [key: string]: string | number | boolean | undefined
} 