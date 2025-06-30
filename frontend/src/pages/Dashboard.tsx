import React from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  CpuChipIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts'
import apiClient from '@/api/client'
import Card from '@/components/ui/Card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

// Mock data for demonstration
const mockMarketData = [
  { date: '2024-01', value: 4200, volume: 1200000 },
  { date: '2024-02', value: 4350, volume: 1350000 },
  { date: '2024-03', value: 4150, volume: 1100000 },
  { date: '2024-04', value: 4500, volume: 1450000 },
  { date: '2024-05', value: 4600, volume: 1500000 },
  { date: '2024-06', value: 4750, volume: 1600000 },
]

const mockCorrelationData = [
  { name: 'AAPL-MSFT', correlation: 0.85, color: '#10b981' },
  { name: 'GOOGL-META', correlation: 0.72, color: '#3b82f6' },
  { name: 'TSLA-NVDA', correlation: 0.68, color: '#8b5cf6' },
  { name: 'JPM-BAC', correlation: 0.91, color: '#f59e0b' },
  { name: 'BTC-ETH', correlation: 0.76, color: '#ef4444' },
]

const mockMetrics = {
  portfolioValue: 125480.50,
  dailyChange: 2340.75,
  changePercent: 1.87,
  totalPatterns: 1247,
  llmQueries: 89,
  correlations: 324,
}

const Dashboard: React.FC = () => {
  // Fetch real-time data
  const { isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000,
  })

  const { data: llmStatus } = useQuery({
    queryKey: ['llm-status'],
    queryFn: () => apiClient.getLLMStatus(),
    refetchInterval: 60000,
  })

  const { data: vectorStats } = useQuery({
    queryKey: ['vector-stats'],
    queryFn: () => apiClient.getVectorStats(),
    refetchInterval: 120000,
  })

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Real-time overview of your multi-market correlation analysis
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Portfolio Value</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${mockMetrics.portfolioValue.toLocaleString()}
                </p>
                <div className="flex items-center mt-1">
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                  <span className="text-sm text-green-600">
                    +${mockMetrics.dailyChange.toLocaleString()} ({mockMetrics.changePercent}%)
                  </span>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Active Correlations</p>
                <p className="text-2xl font-bold text-gray-900">
                  {mockMetrics.correlations}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Across {mockCorrelationData.length} pairs
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CpuChipIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Vector Patterns</p>
                <p className="text-2xl font-bold text-gray-900">
                  {vectorStats?.total_patterns || mockMetrics.totalPatterns}
                </p>
                <div className="flex items-center mt-1">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    vectorStats?.is_trained ? 'bg-green-400' : 'bg-orange-400'
                  }`} />
                  <span className="text-sm text-gray-600">
                    {vectorStats?.index_type || 'FAISS'} Index
                  </span>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">LLM Queries Today</p>
                <p className="text-2xl font-bold text-gray-900">
                  {mockMetrics.llmQueries}
                </p>
                <div className="flex items-center mt-1">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    llmStatus?.model_available ? 'bg-green-400' : 'bg-red-400'
                  }`} />
                  <span className="text-sm text-gray-600">
                    {llmStatus?.model_available ? 'Model Ready' : 'Model Loading'}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Performance Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card title="Market Performance" subtitle="6-month trend">
            {healthLoading ? (
              <div className="h-64 flex items-center justify-center">
                <LoadingSpinner />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockMarketData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#6b7280"
                    fontSize={12}
                  />
                  <YAxis 
                    stroke="#6b7280"
                    fontSize={12}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Card>
        </motion.div>

        {/* Correlation Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card title="Top Correlations" subtitle="Current market pairs">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockCorrelationData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  type="number"
                  domain={[0, 1]}
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis 
                  type="category"
                  dataKey="name"
                  stroke="#6b7280"
                  fontSize={12}
                  width={80}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                  formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Correlation']}
                />
                <Bar dataKey="correlation" radius={[0, 4, 4, 0]}>
                  {mockCorrelationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <Card title="Recent Activity" subtitle="Latest system events">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  New correlation pattern detected between AAPL and MSFT
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Correlation strength: 0.87 • 5 minutes ago
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  Vector database updated with 15 new patterns
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Total patterns: {vectorStats?.total_patterns || mockMetrics.totalPatterns} • 12 minutes ago
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  LLM generated portfolio optimization recommendations
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  3 buy signals, 2 sell signals • 25 minutes ago
                </p>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}

export default Dashboard 