import React, { useState } from 'react'
import {
  ChartBarIcon,
  ArrowTrendingUpIcon as TrendingUpIcon,
  ArrowTrendingDownIcon as TrendingDownIcon,
  ClockIcon,
  CalendarDaysIcon,
  FunnelIcon,
  CogIcon,
  ArrowPathIcon,
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
import Card from '@/components/ui/Card'

const MarketAnalysis: React.FC = () => {
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['AAPL', 'GOOGL'])
  const [timeRange, setTimeRange] = useState<'1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | '2Y'>('1M')
  const [selectedGroup, setSelectedGroup] = useState<string>('Tech Stocks')
  const [startDate, setStartDate] = useState<string>('2024-01-01')
  const [endDate, setEndDate] = useState<string>('2024-06-30')
  const [correlationMethod, setCorrelationMethod] = useState<'pearson' | 'spearman' | 'kendall'>('pearson')
  const [rollingWindow, setRollingWindow] = useState<number>(30)
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('line')

  // Asset groups from your Streamlit dashboard
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

  // Mock data for demonstration
  const priceData = [
    { date: '2024-01-01', AAPL: 150, GOOGL: 2800, MSFT: 320, TSLA: 240 },
    { date: '2024-01-02', AAPL: 152, GOOGL: 2820, MSFT: 325, TSLA: 245 },
    { date: '2024-01-03', AAPL: 148, GOOGL: 2790, MSFT: 318, TSLA: 238 },
    { date: '2024-01-04', AAPL: 155, GOOGL: 2850, MSFT: 330, TSLA: 250 },
    { date: '2024-01-05', AAPL: 157, GOOGL: 2870, MSFT: 335, TSLA: 255 },
    { date: '2024-01-06', AAPL: 159, GOOGL: 2890, MSFT: 340, TSLA: 260 },
  ]

  const correlationData = [
    { symbol: 'AAPL', AAPL: 1.0, GOOGL: 0.75, MSFT: 0.68, TSLA: 0.42 },
    { symbol: 'GOOGL', AAPL: 0.75, GOOGL: 1.0, MSFT: 0.82, TSLA: 0.38 },
    { symbol: 'MSFT', AAPL: 0.68, GOOGL: 0.82, MSFT: 1.0, TSLA: 0.35 },
    { symbol: 'TSLA', AAPL: 0.42, GOOGL: 0.38, MSFT: 0.35, TSLA: 1.0 },
  ]

  const handleSymbolToggle = (symbol: string) => {
    setSelectedSymbols(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    )
  }

  const handleGroupChange = (group: string) => {
    setSelectedGroup(group)
    if (group !== 'Custom') {
      setSelectedSymbols(symbolGroups[group as keyof typeof symbolGroups])
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
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    
    switch (chartType) {
      case 'area':
        return (
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
        )
      case 'bar':
        return (
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
        )
      default:
        return (
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
        <button className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          <ArrowPathIcon className="w-4 h-4 mr-2" />
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
                        ? 'bg-primary-50 border-primary-200 text-primary-700'
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
                      className="inline-flex items-center px-2 py-1 text-xs bg-primary-100 text-primary-800 rounded"
                    >
                      {symbol}
                      <button
                        onClick={() => handleSymbolToggle(symbol)}
                        className="ml-1 text-primary-600 hover:text-primary-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Date Range Configuration */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <CalendarDaysIcon className="w-4 h-4 inline mr-2" />
                Date Range Presets
              </label>
              <div className="grid grid-cols-2 gap-2">
                {Object.keys(datePresets).map((preset) => (
                  <button
                    key={preset}
                    onClick={() => handleDatePreset(preset)}
                    className="px-3 py-2 text-sm rounded border border-gray-200 hover:bg-gray-50 transition-colors"
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
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
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              >
                <option value="pearson">Pearson</option>
                <option value="spearman">Spearman</option>
                <option value="kendall">Kendall</option>
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
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chart Type
              </label>
              <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value as typeof chartType)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
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
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              >
                {timeRangeOptions.map((range) => (
                  <option key={range} value={range}>{range}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Asset Selection */}
      {selectedGroup === 'Custom' && (
        <Card title="Custom Asset Selection" subtitle="Choose individual assets for analysis">
          <div className="flex flex-wrap gap-2">
            {availableSymbols.map((symbol) => (
              <button
                key={symbol}
                onClick={() => handleSymbolToggle(symbol)}
                className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                  selectedSymbols.includes(symbol)
                    ? 'bg-primary-50 border-primary-200 text-primary-700'
                    : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {symbol}
              </button>
            ))}
          </div>
        </Card>
      )}

      {/* Price Chart */}
      <Card 
        title={`Price Performance - ${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart`}
        subtitle={`${timeRange} price movements for selected symbols (${startDate} to ${endDate})`}
      >
        <ResponsiveContainer width="100%" height={400}>
          {renderChart()}
        </ResponsiveContainer>
      </Card>

      {/* Statistics and Correlation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Statistics */}
        <Card title="Market Statistics" subtitle={`Key metrics for selected symbols (${correlationMethod} correlation)`}>
          <div className="space-y-4">
            {selectedSymbols.slice(0, 6).map((symbol, index) => {
              const change = Math.random() > 0.5 ? 1 : -1
              const changePercent = (Math.random() * 5 * change).toFixed(2)
              const price = priceData[priceData.length - 1][symbol as keyof typeof priceData[0]]
              
              return (
                <div key={symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full" style={{ 
                      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'][index % 6] 
                    }} />
                    <span className="font-medium text-gray-900">{symbol}</span>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">${price}</p>
                    <div className={`flex items-center text-sm ${
                      parseFloat(changePercent) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {parseFloat(changePercent) >= 0 ? (
                        <TrendingUpIcon className="w-4 h-4 mr-1" />
                      ) : (
                        <TrendingDownIcon className="w-4 h-4 mr-1" />
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
        <Card title="Correlation Matrix" subtitle={`${correlationMethod} correlation coefficients (${rollingWindow}d rolling window)`}>
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
                      const value = row[symbol as keyof typeof row] as number
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