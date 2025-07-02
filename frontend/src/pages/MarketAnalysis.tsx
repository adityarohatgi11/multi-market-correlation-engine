import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  PlayIcon,
  InformationCircleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  FunnelIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from 'recharts'

// Simple Card Component (inline to avoid import issues)
interface CardProps {
  title?: string
  subtitle?: string
  children: React.ReactNode
  className?: string
}

const Card: React.FC<CardProps> = ({ title, subtitle, children, className = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden ${className}`}
    >
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              {title && (
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              )}
              {subtitle && (
                <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
              )}
            </div>
          </div>
        </div>
      )}
      
      <div className="p-6">
        {children}
      </div>
    </motion.div>
  )
}

const MarketAnalysis: React.FC = () => {
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['AAPL', 'GOOGL'])
  const [timeRange, setTimeRange] = useState<'1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | '2Y'>('1M')
  const [selectedGroup, setSelectedGroup] = useState<string>('Tech Stocks')
  const [startDate, setStartDate] = useState<string>('2024-01-01')
  const [endDate, setEndDate] = useState<string>('2024-06-30')
  const [correlationMethod, setCorrelationMethod] = useState<'pearson' | 'spearman' | 'kendall'>('pearson')
  const [rollingWindow, setRollingWindow] = useState<number>(30)
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('line')
  const [loading, setLoading] = useState<boolean>(false)
  const [priceData, setPriceData] = useState<any[]>([])
  const [correlationData, setCorrelationData] = useState<any[]>([])

  // Asset groups from your backend configuration
  const symbolGroups = {
    "Tech Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"],
    "Financial": ["JPM", "BAC", "GS", "WFC", "C", "MS"],
    "Energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABT", "TMO"],
    "Market Indices": ["SPY", "QQQ", "IWM", "VTI", "EFA"],
    "Commodities": ["GLD", "SLV", "USO", "DBA"],
    "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD"],
    "Consumer Goods": ["WMT", "PG", "KO", "PEP", "COST"],
    "Custom": []
  }

  const availableSymbols = Object.values(symbolGroups).flat().filter((symbol, index, arr) => arr.indexOf(symbol) === index)
  const timeRangeOptions = ['1D', '1W', '1M', '3M', '6M', '1Y', '2Y'] as const

  // Date preset options
  const datePresets = {
    "1 Month": 30,
    "3 Months": 90,
    "6 Months": 180,
    "1 Year": 365,
    "2 Years": 730,
    "5 Years": 1825
  }

  // Initialize mock data on component mount
  useEffect(() => {
    generateMockData()
  }, [selectedSymbols, timeRange])

  const generateMockData = () => {
    setLoading(true)
    
    // Simulate API call delay
    setTimeout(() => {
      try {
        // Generate mock price data based on selected symbols
        const mockPriceData = []
        const baseDate = new Date()
        
        for (let i = 0; i < 30; i++) {
          const date = new Date(baseDate.getTime() - (29 - i) * 24 * 60 * 60 * 1000)
          const dataPoint: any = {
            date: date.toISOString().split('T')[0]
          }
          
          selectedSymbols.forEach((symbol, index) => {
            const basePrice = 100 + (index * 50) + Math.random() * 100
            const variation = Math.sin(i * 0.1) * 10 + Math.random() * 20 - 10
            dataPoint[symbol] = Math.round((basePrice + variation) * 100) / 100
          })
          
          mockPriceData.push(dataPoint)
        }
        
        // Generate mock correlation data
        const mockCorrelationData = selectedSymbols.map(symbol1 => {
          const row: any = { symbol: symbol1 }
          selectedSymbols.forEach(symbol2 => {
            if (symbol1 === symbol2) {
              row[symbol2] = 1.0
            } else {
              // Generate deterministic correlation based on symbol names
              const hash = (symbol1 + symbol2).split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0)
                return a & a
              }, 0)
              row[symbol2] = Math.round((Math.abs(hash) % 100) / 100 * 100) / 100
            }
          })
          return row
        })
        
        setPriceData(mockPriceData)
        setCorrelationData(mockCorrelationData)
      } catch (error) {
        console.error('Error generating mock data:', error)
      } finally {
        setLoading(false)
      }
    }, 500) // 500ms delay to simulate loading
  }

  const handleSymbolToggle = (symbol: string) => {
    const newSelection = selectedSymbols.includes(symbol) 
      ? selectedSymbols.filter(s => s !== symbol)
      : [...selectedSymbols, symbol]
    
    setSelectedSymbols(newSelection)
  }

  const handleGroupChange = (group: string) => {
    setSelectedGroup(group)
    if (group !== 'Custom') {
      const groupSymbols = symbolGroups[group as keyof typeof symbolGroups] || []
      setSelectedSymbols(groupSymbols.slice(0, 4)) // Limit to 4 symbols for better visualization
    }
  }

  const handleDatePreset = (preset: string) => {
    const days = datePresets[preset as keyof typeof datePresets]
    const end = new Date()
    const start = new Date(end.getTime() - (days * 24 * 60 * 60 * 1000))
    
    setEndDate(end.toISOString().split('T')[0])
    setStartDate(start.toISOString().split('T')[0])
  }

  const getCorrelationColor = (value: number) => {
    if (value > 0.7) return '#10b981' // Strong positive
    if (value > 0.3) return '#3b82f6' // Moderate positive
    if (value > -0.3) return '#6b7280' // Weak
    if (value > -0.7) return '#f59e0b' // Moderate negative
    return '#ef4444' // Strong negative
  }

  const renderChart = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading market data...</span>
        </div>
      )
    }

    if (!priceData.length || !selectedSymbols.length) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <ExclamationTriangleIcon className="w-8 h-8 mr-2" />
          <span>No data available for selected symbols</span>
        </div>
      )
    }

    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    
    try {
      switch (chartType) {
        case 'area':
          return (
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip />
                {selectedSymbols.map((symbol, index) => (
                  <Area
                    key={symbol}
                    type="monotone"
                    dataKey={symbol}
                    stackId="1"
                    stroke={colors[index % colors.length]}
                    fill={colors[index % colors.length]}
                    fillOpacity={0.3}
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          )
        case 'bar':
          return (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip />
                {selectedSymbols.map((symbol, index) => (
                  <Bar
                    key={symbol}
                    dataKey={symbol}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          )
        default:
          return (
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                {selectedSymbols.map((symbol, index) => (
                  <Line
                    key={symbol}
                    type="monotone"
                    dataKey={symbol}
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )
      }
    } catch (error) {
      console.error('Error rendering chart:', error)
      return (
        <div className="flex items-center justify-center h-64 text-red-500">
          <ExclamationTriangleIcon className="w-8 h-8 mr-2" />
          <span>Error rendering chart</span>
        </div>
      )
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Market Analysis</h1>
          <p className="text-gray-600 mt-2">
            Advanced market data and correlation analysis with customizable parameters
          </p>
        </div>
        <button 
          onClick={generateMockData}
          disabled={loading}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <ArrowPathIcon className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Data
        </button>
      </div>

      {/* Analysis Configuration */}
      <Card title="Analysis Configuration" subtitle="Configure your market analysis parameters and data sources">
        <div className="space-y-6">
          {/* Asset Group Selection */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <FunnelIcon className="w-4 h-4 inline mr-2" />
                Asset Groups
              </label>
              <div className="grid grid-cols-2 gap-2">
                {Object.keys(symbolGroups).map((group) => (
                  <button
                    key={group}
                    onClick={() => handleGroupChange(group)}
                    className={`p-3 text-sm text-left rounded-lg border transition-colors ${
                      selectedGroup === group
                        ? 'bg-blue-50 border-blue-200 text-blue-700'
                        : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {group}
                    <span className="block text-xs text-gray-500 mt-1">
                      {group === 'Custom' ? 'Manual selection' : `${symbolGroups[group as keyof typeof symbolGroups].length} assets`}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Selected Assets ({selectedSymbols.length})
              </label>
              <div className="max-h-32 overflow-y-auto border rounded-lg p-3 bg-gray-50">
                <div className="flex flex-wrap gap-2">
                  {selectedSymbols.map((symbol) => (
                    <span
                      key={symbol}
                      className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                    >
                      {symbol}
                      <button
                        onClick={() => handleSymbolToggle(symbol)}
                        className="ml-1 text-blue-600 hover:text-blue-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Analysis Parameters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Correlation Method
              </label>
              <select
                value={correlationMethod}
                onChange={(e) => setCorrelationMethod(e.target.value as typeof correlationMethod)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="pearson">Pearson</option>
                <option value="spearman">Spearman</option>
                <option value="kendall">Kendall</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chart Type
              </label>
              <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value as typeof chartType)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="line">Line Chart</option>
                <option value="area">Area Chart</option>
                <option value="bar">Bar Chart</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Range
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value as typeof timeRange)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {timeRangeOptions.map((range) => (
                  <option key={range} value={range}>{range}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rolling Window
              </label>
              <input
                type="number"
                min="5"
                max="100"
                value={rollingWindow}
                onChange={(e) => setRollingWindow(parseInt(e.target.value))}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Price Chart */}
      <Card 
        title={`Price Performance - ${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart`}
        subtitle={`${timeRange} price movements for selected symbols`}
      >
        {renderChart()}
      </Card>

      {/* Statistics and Correlation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Statistics */}
        <Card title="Market Statistics" subtitle={`Key metrics for selected symbols`}>
          <div className="space-y-4">
            {selectedSymbols.slice(0, 6).map((symbol, index) => {
              const change = Math.random() > 0.5 ? 1 : -1
              const changePercent = (Math.random() * 5 * change).toFixed(2)
              const price = priceData.length > 0 ? priceData[priceData.length - 1][symbol] || 100 : 100
              
              return (
                <div key={symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full" style={{ 
                      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'][index % 6] 
                    }} />
                    <span className="font-medium text-gray-900">{symbol}</span>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">${price.toFixed(2)}</p>
                    <div className={`flex items-center text-sm ${
                      parseFloat(changePercent) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {parseFloat(changePercent) >= 0 ? (
                        <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
                      ) : (
                        <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />
                      )}
                      {changePercent}%
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </Card>

        {/* Correlation Matrix */}
        <Card title="Correlation Matrix" subtitle={`${correlationMethod} correlation coefficients`}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left p-2 text-sm font-medium text-gray-700"></th>
                  {selectedSymbols.slice(0, 4).map((symbol) => (
                    <th key={symbol} className="text-center p-2 text-sm font-medium text-gray-700">
                      {symbol}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {correlationData.slice(0, Math.min(4, selectedSymbols.length)).map((row) => (
                  <tr key={row.symbol}>
                    <td className="p-2 text-sm font-medium text-gray-900">{row.symbol}</td>
                    {selectedSymbols.slice(0, 4).map((symbol) => {
                      const value = row[symbol as keyof typeof row] as number || 0
                      return (
                        <td key={symbol} className="p-2 text-center">
                          <span
                            className="inline-block px-2 py-1 rounded text-xs font-medium text-white"
                            style={{ backgroundColor: getCorrelationColor(value) }}
                          >
                            {value.toFixed(2)}
                          </span>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Analysis Summary */}
      <Card title="Analysis Summary" subtitle="Key insights from current configuration">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{selectedSymbols.length}</div>
            <div className="text-sm text-blue-700">Assets Selected</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{correlationMethod}</div>
            <div className="text-sm text-green-700">Correlation Method</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{rollingWindow}d</div>
            <div className="text-sm text-purple-700">Rolling Window</div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default MarketAnalysis 