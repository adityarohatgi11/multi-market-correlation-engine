import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  CogIcon,
  ChartBarIcon,
  CpuChipIcon,
  ClockIcon,
  ShieldCheckIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline'
import Card from '@/components/ui/Card'

const Settings: React.FC = () => {
  const [selectedAnalysisType, setSelectedAnalysisType] = useState('overview')
  const [correlationMethod, setCorrelationMethod] = useState('pearson')
  const [rollingWindow, setRollingWindow] = useState(30)
  const [selectedStrategy, setSelectedStrategy] = useState('balanced')
  const [investmentHorizon, setInvestmentHorizon] = useState('3M')

  const analysisTypes = [
    { id: 'overview', name: '📊 Overview', description: 'General market analysis' },
    { id: 'garch', name: '📈 GARCH Models', description: 'Volatility modeling' },
    { id: 'var', name: '🔄 VAR Analysis', description: 'Vector autoregression' },
    { id: 'ml', name: '🤖 Machine Learning', description: 'ML correlation prediction' },
    { id: 'network', name: '🌐 Network Analysis', description: 'Asset network topology' },
    { id: 'regime', name: '🎯 Regime Detection', description: 'Market regime identification' }
  ]

  const assetGroups = {
    "Tech Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"],
    "Financial": ["JPM", "BAC", "GS", "WFC", "C", "MS"],
    "Energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABT", "TMO"],
    "Consumer Goods": ["WMT", "PG", "KO", "PEP", "COST"],
    "Commodities": ["GLD", "SLV", "USO", "DBA"],
    "Indices": ["SPY", "QQQ", "IWM", "VTI", "EFA"],
    "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD"]
  }

  const strategies = {
    conservative: { name: '🛡️ Conservative', description: 'Low risk, stable returns' },
    balanced: { name: '⚖️ Balanced', description: 'Moderate risk-return balance' },
    aggressive: { name: '🚀 Aggressive', description: 'High risk, high potential returns' },
    diversified: { name: '🌐 Diversified', description: 'Broad market exposure' }
  }

  const timeHorizons = ['1D', '1W', '1M', '3M', '6M', '1Y', '2Y']

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings & Configuration</h1>
        <p className="text-gray-600 mt-2">
          Configure analysis parameters, model settings, and trading strategies
        </p>
      </div>

      {/* Analysis Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card title="Analysis Configuration" subtitle="Select analysis type and parameters">
          <div className="space-y-6">
            {/* Analysis Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <ChartBarIcon className="w-5 h-5 inline mr-2" />
                Analysis Type
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {analysisTypes.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setSelectedAnalysisType(type.id)}
                    className={`p-4 text-left rounded-lg border transition-all ${
                      selectedAnalysisType === type.id
                        ? 'bg-primary-50 border-primary-200 ring-2 ring-primary-500'
                        : 'bg-white border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{type.name}</div>
                    <div className="text-sm text-gray-500 mt-1">{type.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Correlation Method */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Correlation Method
                </label>
                <select
                  value={correlationMethod}
                  onChange={(e) => setCorrelationMethod(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  <option value="pearson">Pearson</option>
                  <option value="spearman">Spearman</option>
                  <option value="kendall">Kendall</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rolling Window (days)
                </label>
                <input
                  type="range"
                  min="10"
                  max="100"
                  value={rollingWindow}
                  onChange={(e) => setRollingWindow(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="text-sm text-gray-600 mt-1">{rollingWindow} days</div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Investment Horizon
                </label>
                <select
                  value={investmentHorizon}
                  onChange={(e) => setInvestmentHorizon(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  {timeHorizons.map((horizon) => (
                    <option key={horizon} value={horizon}>{horizon}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Asset Categories */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card title="Asset Categories" subtitle="Pre-configured asset groups for analysis">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(assetGroups).map(([groupName, symbols]) => (
              <div key={groupName} className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">{groupName}</h4>
                <div className="text-sm text-gray-600 mb-3">
                  {symbols.length} assets
                </div>
                <div className="flex flex-wrap gap-1">
                  {symbols.slice(0, 5).map((symbol) => (
                    <span
                      key={symbol}
                      className="inline-block px-2 py-1 text-xs bg-white rounded border"
                    >
                      {symbol}
                    </span>
                  ))}
                  {symbols.length > 5 && (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-200 rounded">
                      +{symbols.length - 5}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Strategy Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card title="Investment Strategy" subtitle="Choose your risk tolerance and investment approach">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(strategies).map(([key, strategy]) => (
                <button
                  key={key}
                  onClick={() => setSelectedStrategy(key)}
                  className={`p-4 text-left rounded-lg border transition-all ${
                    selectedStrategy === key
                      ? 'bg-primary-50 border-primary-200 ring-2 ring-primary-500'
                      : 'bg-white border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-medium text-gray-900">{strategy.name}</div>
                  <div className="text-sm text-gray-500 mt-1">{strategy.description}</div>
                </button>
              ))}
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Model Parameters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card title="Model Parameters" subtitle="Advanced configuration for ML and statistical models">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* GARCH Parameters */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900 flex items-center">
                <CpuChipIcon className="w-5 h-5 mr-2" />
                GARCH Model
              </h4>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Model Order (p,q)</label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    min="1"
                    max="5"
                    defaultValue="1"
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                    placeholder="p"
                  />
                  <input
                    type="number"
                    min="1"
                    max="5"
                    defaultValue="1"
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                    placeholder="q"
                  />
                </div>
              </div>
            </div>

            {/* VAR Parameters */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900 flex items-center">
                <AdjustmentsHorizontalIcon className="w-5 h-5 mr-2" />
                VAR Model
              </h4>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Max Lags</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  defaultValue="5"
                  className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                />
              </div>
            </div>

            {/* ML Parameters */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900 flex items-center">
                <CogIcon className="w-5 h-5 mr-2" />
                ML Models
              </h4>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Lookback Period</label>
                <input
                  type="number"
                  min="30"
                  max="365"
                  defaultValue="60"
                  className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                />
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* System Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card title="System Settings" subtitle="API configuration and performance settings">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900 flex items-center">
                <ClockIcon className="w-5 h-5 mr-2" />
                Data Collection
              </h4>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Update Frequency</label>
                <select className="w-full rounded border border-gray-300 px-2 py-1 text-sm">
                  <option value="real-time">Real-time</option>
                  <option value="1min">1 Minute</option>
                  <option value="5min">5 Minutes</option>
                  <option value="15min">15 Minutes</option>
                  <option value="1hour">1 Hour</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium text-gray-900 flex items-center">
                <ShieldCheckIcon className="w-5 h-5 mr-2" />
                Security
              </h4>
              <div>
                <label className="block text-sm text-gray-600 mb-1">API Rate Limiting</label>
                <select className="w-full rounded border border-gray-300 px-2 py-1 text-sm">
                  <option value="standard">Standard (100/min)</option>
                  <option value="premium">Premium (500/min)</option>
                  <option value="enterprise">Enterprise (Unlimited)</option>
                </select>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Save Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex justify-end space-x-4"
      >
        <button className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
          Reset to Defaults
        </button>
        <button className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          Save Configuration
        </button>
      </motion.div>
    </div>
  )
}

export default Settings 