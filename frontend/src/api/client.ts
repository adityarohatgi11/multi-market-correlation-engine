import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import toast from 'react-hot-toast'
import type {
  ApiResponse,
  MarketData,
  Recommendation,
  RecommendationRequest,
  VectorPattern,
  VectorSearchRequest,
  VectorStoreRequest,
  VectorStats,
  LLMStatus,
  ChatRequest,
  ChatMessage,
  MarketAnalysisRequest,
  MarketAnalysis,
  QueryParams,
} from '../types'

class ApiClient {
  private instance: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL
    this.instance = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  get apiBaseURL(): string {
    return this.baseURL
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        // Add loading state or authentication here
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('Request error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error) => {
        const errorMessage = error.response?.data?.detail || error.message || 'An error occurred'
        
        // Don't show error toast for certain endpoints (like health checks)
        if (!error.config?.url?.includes('/health')) {
          toast.error(errorMessage)
        }
        
        console.error('API Error:', {
          url: error.config?.url,
          status: error.response?.status,
          message: errorMessage,
        })
        
        return Promise.reject(error)
      }
    )
  }

  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.request<ApiResponse<T>>(config)
    return (response.data as any).data || response.data as T
  }

  // Generic HTTP methods
  async get<T>(url: string, params?: QueryParams): Promise<T> {
    return this.request({
      method: 'GET',
      url,
      params,
    })
  }

  async post<T>(url: string, data?: any, params?: QueryParams): Promise<T> {
    return this.request({
      method: 'POST',
      url,
      data,
      params,
    })
  }

  async put<T>(url: string, data?: any, params?: QueryParams): Promise<T> {
    return this.request({
      method: 'PUT',
      url,
      data,
      params,
    })
  }

  async delete<T>(url: string, params?: QueryParams): Promise<T> {
    return this.request({
      method: 'DELETE',
      url,
      params,
    })
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request({
      method: 'GET',
      url: '/health',
    })
  }

  // Market Data Endpoints
  async getMarketData(
    symbols: string[],
    timeRange: string = '1Y',
    params?: QueryParams
  ): Promise<MarketData[]> {
    return this.request({
      method: 'GET',
      url: '/market/data',
      params: {
        symbols: symbols.join(','),
        time_range: timeRange,
        ...params,
      },
    })
  }

  async getCorrelationMatrix(symbols: string[], timeRange: string = '1Y'): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/market/correlation',
      data: {
        symbols,
        time_range: timeRange,
      },
    })
  }

  // Recommendation Endpoints
  async generateRecommendations(request: RecommendationRequest): Promise<Recommendation[]> {
    return this.request({
      method: 'POST',
      url: '/recommendations/generate',
      data: request,
    })
  }

  async getRecommendationHistory(
    limit: number = 10,
    offset: number = 0
  ): Promise<Recommendation[]> {
    return this.request({
      method: 'GET',
      url: '/recommendations/history',
      params: { limit, offset },
    })
  }

  // LLM Endpoints
  async getLLMStatus(): Promise<LLMStatus> {
    return this.request({
      method: 'GET',
      url: '/llm/status',
    })
  }

  async sendChatMessage(request: ChatRequest): Promise<ChatMessage> {
    return this.request({
      method: 'POST',
      url: '/llm/chat',
      data: request,
    })
  }

  async generateMarketAnalysis(request: MarketAnalysisRequest): Promise<MarketAnalysis> {
    return this.request({
      method: 'POST',
      url: '/llm/analyze/market',
      data: request,
    })
  }

  async explainCorrelations(
    correlationMatrix: any,
    symbols: string[],
    timePeriod: string = 'recent'
  ): Promise<{ analysis: string; insights: string[] }> {
    return this.request({
      method: 'POST',
      url: '/llm/analyze/correlations',
      data: {
        correlation_matrix: correlationMatrix,
        symbols,
        time_period: timePeriod,
      },
    })
  }

  async explainRecommendations(
    recommendations: Recommendation[],
    portfolio: any,
    marketConditions: string = ''
  ): Promise<{ explanation: string; reasoning: string[] }> {
    return this.request({
      method: 'POST',
      url: '/llm/explain/recommendations',
      data: {
        recommendations,
        portfolio,
        market_conditions: marketConditions,
      },
    })
  }

  // Vector Database Endpoints
  async getVectorStats(): Promise<VectorStats> {
    return this.request({
      method: 'GET',
      url: '/llm/vector/stats',
    })
  }

  async searchVectorPatterns(request: VectorSearchRequest): Promise<VectorPattern[]> {
    return this.request({
      method: 'POST',
      url: '/llm/vector/search',
      data: request,
    })
  }

  async storeVectorPattern(request: VectorStoreRequest): Promise<{ success: boolean; message: string }> {
    return this.request({
      method: 'POST',
      url: '/llm/vector/store',
      data: request,
    })
  }

  async clearVectorDatabase(): Promise<{ success: boolean; message: string }> {
    return this.request({
      method: 'DELETE',
      url: '/llm/vector/clear',
    })
  }

  // ML Model Endpoints
  async getPredictions(symbols: string[], model: string = 'lstm'): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/ml/predict',
      data: {
        symbols,
        model_type: model,
      },
    })
  }

  async getRegimeAnalysis(symbols: string[]): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/ml/regime',
      data: {
        symbols,
      },
    })
  }

  // Utility Methods
  async uploadFile(file: File, endpoint: string): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)

    return this.request({
      method: 'POST',
      url: endpoint,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  }

  async downloadReport(type: string, params?: QueryParams): Promise<Blob> {
    const response = await this.instance.request({
      method: 'GET',
      url: `/reports/${type}`,
      params,
      responseType: 'blob',
    })
    return response.data
  }

  // Real-time updates (placeholder for WebSocket integration)
  async subscribeToUpdates(symbols: string[], callback: (data: any) => void): Promise<() => void> {
    // This would typically connect to a WebSocket
    // For now, we'll simulate with polling
    const interval = setInterval(async () => {
      try {
        const data = await this.getMarketData(symbols, '1D')
        callback(data)
      } catch (error) {
        console.error('Real-time update error:', error)
      }
    }, 30000) // Update every 30 seconds

    // Return cleanup function
    return () => clearInterval(interval)
  }
}

// Create and export a default instance
const apiClient = new ApiClient()

export default apiClient

// Export the class for custom instances
export { ApiClient } 