import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  CpuChipIcon,
  ChartBarIcon,
  CogIcon,
  ArrowPathIcon,
  BeakerIcon,
  AcademicCapIcon,
  LightBulbIcon,
  PlayIcon,
} from '@heroicons/react/24/outline';
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
  ScatterChart,
  Scatter,
  BarChart,
  Bar,
} from 'recharts';
import Card from '@/components/ui/Card';

const Analysis: React.FC = () => {
  const [selectedAnalysisType, setSelectedAnalysisType] = useState('overview');
  const [selectedSymbols, setSelectedSymbols] = useState(['AAPL', 'MSFT', 'GOOGL']);
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const analysisTypes = [
    {
      id: 'overview',
      name: '📊 Overview',
      description: 'General market correlation analysis',
      color: 'blue',
      icon: ChartBarIcon
    },
    {
      id: 'garch',
      name: '📈 GARCH Models',
      description: 'Volatility modeling and forecasting',
      color: 'green',
      icon: BeakerIcon
    },
    {
      id: 'var',
      name: '🔄 VAR Analysis',
      description: 'Vector autoregression modeling',
      color: 'purple',
      icon: CogIcon
    },
    {
      id: 'ml',
      name: '🤖 Machine Learning',
      description: 'ML correlation prediction with Random Forest and LSTM',
      color: 'orange',
      icon: CpuChipIcon
    },
    {
      id: 'network',
      name: '🌐 Network Analysis',
      description: 'Asset network topology and centrality metrics',
      color: 'indigo',
      icon: AcademicCapIcon
    },
    {
      id: 'regime',
      name: '🎯 Regime Detection',
      description: 'Market regime identification using clustering',
      color: 'pink',
      icon: LightBulbIcon
    }
  ];

  const availableSymbols = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
    'JPM', 'BAC', 'GS', 'WFC', 'C', 'MS',
    'XOM', 'CVX', 'COP', 'EOG', 'SLB',
    'JNJ', 'UNH', 'PFE', 'ABT', 'TMO'
  ];

  // Mock data for demonstration
  const mockGarchData = [
    { date: '2024-01', volatility: 0.15, forecast: 0.16 },
    { date: '2024-02', volatility: 0.18, forecast: 0.17 },
    { date: '2024-03', volatility: 0.14, forecast: 0.15 },
    { date: '2024-04', volatility: 0.20, forecast: 0.19 },
    { date: '2024-05', volatility: 0.17, forecast: 0.16 },
    { date: '2024-06', volatility: 0.16, forecast: 0.15 },
  ];

  const mockMLPerformance = [
    { model: 'Random Forest', testR2: 0.756, testMSE: 0.0234, trainR2: 0.823 },
    { model: 'LSTM', testR2: 0.692, testMSE: 0.0287, trainR2: 0.778 },
    { model: 'Linear Regression', testR2: 0.534, testMSE: 0.0445, trainR2: 0.567 },
  ];

  const mockRegimeData = [
    { date: '2024-01', regime: 1, confidence: 0.85 },
    { date: '2024-02', regime: 1, confidence: 0.92 },
    { date: '2024-03', regime: 2, confidence: 0.78 },
    { date: '2024-04', regime: 2, confidence: 0.88 },
    { date: '2024-05', regime: 3, confidence: 0.81 },
    { date: '2024-06', regime: 1, confidence: 0.87 },
  ];

  const handleSymbolToggle = (symbol: string) => {
    setSelectedSymbols(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    );
  };

  const runAnalysis = async () => {
    setIsRunning(true);
    
    // Simulate API call
    setTimeout(() => {
      setResults({
        type: selectedAnalysisType,
        symbols: selectedSymbols,
        timestamp: new Date().toISOString(),
        status: 'completed'
      });
      setIsRunning(false);
    }, 3000);
  };

  const renderAnalysisContent = () => {
    switch (selectedAnalysisType) {
      case 'garch':
        return (
          <div className="space-y-6">
            <Card title="GARCH Model Configuration" subtitle="Configure volatility modeling parameters">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model Order (p)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    defaultValue="1"
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model Order (q)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    defaultValue="1"
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Distribution
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="normal">Normal</option>
                    <option value="t">Student's t</option>
                    <option value="skewt">Skewed t</option>
                  </select>
                </div>
              </div>
            </Card>

            {results && results.type === 'garch' && (
              <Card title="GARCH Results" subtitle="Volatility forecasting and analysis">
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={mockGarchData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="volatility" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="forecast" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            )}
          </div>
        );

      case 'var':
        return (
          <div className="space-y-6">
            <Card title="VAR Model Configuration" subtitle="Vector autoregression parameters">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Lags
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    defaultValue="5"
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Information Criterion
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="aic">AIC</option>
                    <option value="bic">BIC</option>
                    <option value="hqic">HQIC</option>
                  </select>
                </div>
              </div>
            </Card>

            {results && results.type === 'var' && (
              <Card title="VAR Analysis Results" subtitle="Vector autoregression model output">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">
                    VAR model successfully fitted with {selectedSymbols.length} variables.
                    Optimal lag order: 3 (based on AIC criterion).
                  </p>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm font-medium text-gray-700">R-squared (avg):</span>
                      <span className="ml-2 text-sm text-gray-900">0.742</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-700">Log Likelihood:</span>
                      <span className="ml-2 text-sm text-gray-900">1,247.3</span>
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </div>
        );

      case 'ml':
        return (
          <div className="space-y-6">
            <Card title="Machine Learning Configuration" subtitle="Configure ML models for correlation prediction">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Lookback Period (days)
                  </label>
                  <input
                    type="number"
                    min="30"
                    max="365"
                    defaultValue="60"
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Train/Test Split
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="0.8">80% / 20%</option>
                    <option value="0.7">70% / 30%</option>
                    <option value="0.6">60% / 40%</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cross Validation
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="5">5-Fold</option>
                    <option value="10">10-Fold</option>
                    <option value="none">None</option>
                  </select>
                </div>
              </div>
            </Card>

            {results && results.type === 'ml' && (
              <Card title="ML Model Performance" subtitle="Comparison of machine learning models">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3 text-sm font-medium text-gray-700">Model</th>
                        <th className="text-center p-3 text-sm font-medium text-gray-700">Test R²</th>
                        <th className="text-center p-3 text-sm font-medium text-gray-700">Test MSE</th>
                        <th className="text-center p-3 text-sm font-medium text-gray-700">Train R²</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockMLPerformance.map((model, index) => (
                        <tr key={index} className="border-b">
                          <td className="p-3 text-sm font-medium text-gray-900">{model.model}</td>
                          <td className="p-3 text-center text-sm text-gray-900">{model.testR2.toFixed(3)}</td>
                          <td className="p-3 text-center text-sm text-gray-900">{model.testMSE.toFixed(4)}</td>
                          <td className="p-3 text-center text-sm text-gray-900">{model.trainR2.toFixed(3)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </div>
        );

      case 'regime':
        return (
          <div className="space-y-6">
            <Card title="Regime Detection Configuration" subtitle="Market regime identification parameters">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Number of Regimes
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="2">2 Regimes</option>
                    <option value="3">3 Regimes</option>
                    <option value="4">4 Regimes</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Clustering Method
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="kmeans">K-Means</option>
                    <option value="hmm">Hidden Markov Model</option>
                    <option value="dbscan">DBSCAN</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Feature Set
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="returns">Returns</option>
                    <option value="volatility">Volatility</option>
                    <option value="both">Both</option>
                  </select>
                </div>
              </div>
            </Card>

            {results && results.type === 'regime' && (
              <Card title="Regime Detection Results" subtitle="Identified market regimes over time">
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart data={mockRegimeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 4]} />
                    <Tooltip />
                    <Scatter dataKey="regime" fill="#8b5cf6" />
                  </ScatterChart>
                </ResponsiveContainer>
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-bold text-blue-600">3</div>
                    <div className="text-sm text-blue-700">Regimes Detected</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-xl font-bold text-green-600">0.84</div>
                    <div className="text-sm text-green-700">Avg Confidence</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-bold text-purple-600">0.73</div>
                    <div className="text-sm text-purple-700">Silhouette Score</div>
                  </div>
                </div>
              </Card>
            )}
          </div>
        );

      case 'network':
        return (
          <div className="space-y-6">
            <Card title="Network Analysis Configuration" subtitle="Asset network topology analysis">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Correlation Threshold
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    defaultValue="0.5"
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Layout Algorithm
                  </label>
                  <select className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                    <option value="spring">Spring Layout</option>
                    <option value="circular">Circular Layout</option>
                    <option value="kamada">Kamada-Kawai</option>
                  </select>
                </div>
              </div>
            </Card>

            {results && results.type === 'network' && (
              <Card title="Network Analysis Results" subtitle="Asset network centrality metrics">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-4">
                    Network analysis completed for {selectedSymbols.length} assets.
                  </p>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-900">12</div>
                      <div className="text-xs text-gray-600">Connections</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-900">0.67</div>
                      <div className="text-xs text-gray-600">Density</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-900">2.4</div>
                      <div className="text-xs text-gray-600">Avg Degree</div>
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </div>
        );

      default:
        return (
          <Card title="Overview Analysis" subtitle="General market correlation analysis">
            <div className="text-center py-8">
              <ChartBarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">
                Select an analysis type from the options above to get started with advanced analytics.
              </p>
            </div>
          </Card>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
          <p className="text-gray-600 mt-2">
            Sophisticated modeling and analysis tools for market correlation research
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={runAnalysis}
            disabled={isRunning || selectedSymbols.length < 2}
            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
              isRunning || selectedSymbols.length < 2
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {isRunning ? (
              <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <PlayIcon className="w-4 h-4 mr-2" />
            )}
            {isRunning ? 'Running Analysis...' : 'Run Analysis'}
          </button>
        </div>
      </div>

      {/* Analysis Type Selection */}
      <Card title="Analysis Type" subtitle="Choose the type of advanced analysis to perform">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analysisTypes.map((type) => (
            <motion.button
              key={type.id}
              onClick={() => setSelectedAnalysisType(type.id)}
              className={`p-4 text-left rounded-lg border-2 transition-all ${
                selectedAnalysisType === type.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center mb-2">
                <type.icon className="w-6 h-6 text-primary-600 mr-2" />
                <h3 className="font-medium text-gray-900">{type.name}</h3>
              </div>
              <p className="text-sm text-gray-600">{type.description}</p>
            </motion.button>
          ))}
        </div>
      </Card>

      {/* Asset Selection */}
      <Card title="Asset Selection" subtitle="Choose assets for analysis (minimum 2 required)">
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {selectedSymbols.map((symbol) => (
              <span
                key={symbol}
                className="inline-flex items-center px-3 py-1 text-sm bg-primary-100 text-primary-800 rounded-full"
              >
                {symbol}
                <button
                  onClick={() => handleSymbolToggle(symbol)}
                  className="ml-2 text-primary-600 hover:text-primary-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          
          <div className="flex flex-wrap gap-2">
            {availableSymbols
              .filter(symbol => !selectedSymbols.includes(symbol))
              .map((symbol) => (
                <button
                  key={symbol}
                  onClick={() => handleSymbolToggle(symbol)}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                >
                  {symbol}
                </button>
              ))}
          </div>
        </div>
      </Card>

      {/* Analysis Content */}
      <motion.div
        key={selectedAnalysisType}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {renderAnalysisContent()}
      </motion.div>

      {/* Analysis Status */}
      {isRunning && (
        <Card title="Analysis Status" subtitle="Running advanced analytics...">
          <div className="flex items-center space-x-4">
            <ArrowPathIcon className="w-6 h-6 text-primary-600 animate-spin" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                Running {analysisTypes.find(t => t.id === selectedAnalysisType)?.name} analysis...
              </p>
              <p className="text-sm text-gray-600">
                Processing {selectedSymbols.length} assets. This may take a few minutes.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Analysis;
