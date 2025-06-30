import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  EyeIcon,
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
  Area
} from 'recharts';

interface MarketMover {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  sparkline: number[];
}

interface Position {
  symbol: string;
  quantity: number;
  marketValue: number;
  dayReturn: number;
  dayReturnPercent: number;
}

const TradingDashboard: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('HMNI');
  const [chartData, setChartData] = useState<any[]>([]);
  const [marketMovers, setMarketMovers] = useState<MarketMover[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [recentOrders, setRecentOrders] = useState<any[]>([]);

  // Generate sample chart data
  useEffect(() => {
    const generateChartData = () => {
      const data = [];
      let basePrice = 183.86;
      for (let i = 0; i < 100; i++) {
        basePrice += (Math.random() - 0.5) * 2;
        data.push({
          time: `${i}`,
          price: Number(basePrice.toFixed(2)),
          volume: Math.floor(Math.random() * 1000000)
        });
      }
      return data;
    };

    setChartData(generateChartData());

    // Sample market movers
    setMarketMovers([
      { symbol: 'HMNI', price: 183.86, change: 3.65, changePercent: 1.36, sparkline: [180, 182, 181, 183, 184] },
      { symbol: 'AAPL', price: 300.17, change: 40.92, changePercent: 18.11, sparkline: [260, 270, 285, 295, 300] },
      { symbol: 'EAIT', price: 189.18, change: 9.20, changePercent: 0.23, sparkline: [180, 182, 186, 188, 189] },
      { symbol: 'WMT', price: 263.74, change: 16.63, changePercent: 4.22, sparkline: [247, 252, 258, 261, 264] },
      { symbol: 'TISM', price: 15.03, change: -0.08, changePercent: -0.03, sparkline: [15.2, 15.1, 15.05, 15.02, 15.03] },
      { symbol: 'UBC', price: 13.16, change: -1.07, changePercent: -5.18, sparkline: [14.5, 14.2, 13.8, 13.4, 13.16] },
      { symbol: 'ICME', price: 401.14, change: 60.02, changePercent: 4.38, sparkline: [340, 360, 380, 395, 401] },
      { symbol: 'BTP', price: 199.21, change: 19.00, changePercent: 5.77, sparkline: [180, 185, 190, 195, 199] },
      { symbol: 'TTCF', price: 62.44, change: -9.16, changePercent: -1.20, sparkline: [72, 68, 65, 63, 62] },
      { symbol: 'SDMF', price: 201.76, change: 1.02, changePercent: 0.02, sparkline: [200, 201, 200.5, 201.2, 201.76] },
      { symbol: 'NKML', price: 37.03, change: -0.59, changePercent: -0.31, sparkline: [38, 37.8, 37.5, 37.2, 37.03] },
      { symbol: 'LLAB', price: 83.74, change: 0.63, changePercent: 1.27, sparkline: [83, 83.2, 83.5, 83.6, 83.74] }
    ]);

    // Sample positions
    setPositions([
      { symbol: 'AAPL', quantity: 1.031, marketValue: 139.01, dayReturn: 2.01, dayReturnPercent: 1.45 },
      { symbol: 'SFFT', quantity: 11.43, marketValue: 5439.91, dayReturn: 237.85, dayReturnPercent: 4.56 },
      { symbol: 'HMNI 10/17 $105 Call', quantity: 2, marketValue: 10439.91, dayReturn: 532.68, dayReturnPercent: 5.38 },
      { symbol: 'HMNI', quantity: 2.04, marketValue: 10439.91, dayReturn: 532.68, dayReturnPercent: 5.38 },
      { symbol: 'LLAB', quantity: 2.04, marketValue: 439.91, dayReturn: 12.01, dayReturnPercent: 2.80 },
      { symbol: 'EEPO 10/19 $56 Put', quantity: 1, marketValue: 10439.91, dayReturn: 532.68, dayReturnPercent: 5.38 },
      { symbol: 'RALI Call Credit Spread', quantity: 1, marketValue: 439.91, dayReturn: 20.01, dayReturnPercent: 4.76 },
      { symbol: 'ICCI', quantity: 3.56, marketValue: 885.35, dayReturn: 97.01, dayReturnPercent: 12.27 },
      { symbol: 'STO', quantity: 44.58, marketValue: 9439.91, dayReturn: 188.69, dayReturnPercent: 2.04 }
    ]);

    // Sample recent orders
    setRecentOrders([
      { symbol: 'LLAB', status: 'Working', side: 'Sell', type: 'Market', quantity: 2 },
      { symbol: 'HMNI', status: 'Filled', side: 'Buy', type: 'Market', quantity: 1 },
      { symbol: 'SFFT Call Debit Spread', status: 'Filled', side: 'Sell', type: 'Limit', quantity: 1 },
      { symbol: 'EAIT', status: 'Cancelled', side: 'Sell', type: 'Stop market', quantity: 1 },
      { symbol: 'ICCI', status: 'Filled', side: 'Buy', type: 'Stop market', quantity: 1 },
      { symbol: 'HMNI', status: 'Filled', side: 'Sell', type: 'Limit', quantity: 1 },
      { symbol: 'HMNI 10/17 $105 Call', status: 'Filled', side: 'Buy', type: 'Limit', quantity: 1 }
    ]);
  }, []);

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`;
  };

  const formatChange = (change: number, changePercent: number) => {
    const isPositive = change >= 0;
    const color = isPositive ? 'text-success-400' : 'text-danger-400';
    const icon = isPositive ? '+' : '';
    
    return (
      <span className={`${color} font-mono text-sm`}>
        {icon}{change.toFixed(2)} ({icon}{changePercent.toFixed(2)}%)
      </span>
    );
  };

  return (
    <div className="h-full bg-dark-950 p-6 overflow-auto">
      <div className="grid grid-cols-12 gap-6 h-full">
        {/* Left Column - Market Movers */}
        <div className="col-span-3 space-y-4">
          <div className="trading-card h-fit">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Market movers</h3>
              <button className="text-primary-400 hover:text-primary-300 text-sm">
                View all
              </button>
            </div>
            
            <div className="space-y-3">
              {marketMovers.map((stock, index) => (
                <motion.div
                  key={stock.symbol}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center justify-between p-3 rounded-lg bg-dark-800/30 hover:bg-dark-800/50 transition-colors cursor-pointer"
                  onClick={() => setSelectedSymbol(stock.symbol)}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-sm">
                      <span className="font-medium text-white">{index + 1}</span>
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-white">{stock.symbol}</span>
                        <div className="w-8 h-4">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={stock.sparkline.map((price, i) => ({ price, index: i }))}>
                              <Line 
                                type="monotone" 
                                dataKey="price" 
                                stroke={stock.change >= 0 ? '#22c55e' : '#ef4444'} 
                                strokeWidth={1}
                                dot={false}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                      <div className="text-xs text-gray-400">Last {formatPrice(stock.price)}</div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-400">Net ch.</div>
                    <div className="text-sm font-medium text-gray-400">Change %</div>
                  </div>
                  
                  <div className="text-right">
                    {formatChange(stock.change, stock.changePercent)}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Center Column - Main Chart */}
        <div className="col-span-6 space-y-4">
          {/* Stock Header */}
          <div className="trading-card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <h2 className="text-2xl font-bold text-white">{selectedSymbol}</h2>
                <span className="text-lg font-mono text-white">$183.86</span>
                <span className="text-success-400 font-mono">+$3.65 (+0.3%)</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <button className="trading-button-success">Buy</button>
                <button className="trading-button-danger">Sell</button>
              </div>
            </div>

            {/* Time intervals */}
            <div className="flex space-x-1 mb-4">
              {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map((interval) => (
                <button
                  key={interval}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    interval === '1D' 
                      ? 'bg-primary-600 text-white' 
                      : 'text-gray-400 hover:text-white hover:bg-dark-800'
                  }`}
                >
                  {interval}
                </button>
              ))}
            </div>
          </div>

          {/* Chart */}
          <div className="trading-card h-96">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="time" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#9ca3af', fontSize: 12 }}
                />
                <YAxis 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#9ca3af', fontSize: 12 }}
                  domain={['dataMin - 1', 'dataMax + 1']}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorPrice)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Volume Chart */}
          <div className="trading-card h-32">
            <h4 className="text-sm font-medium text-gray-400 mb-2">Volume</h4>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <Area 
                  type="monotone" 
                  dataKey="volume" 
                  stroke="#6b7280" 
                  fill="#6b7280" 
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Column - Positions & Orders */}
        <div className="col-span-3 space-y-4">
          {/* Positions */}
          <div className="trading-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Positions</h3>
              <EyeIcon className="w-5 h-5 text-gray-400" />
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {positions.map((position, index) => (
                <motion.div
                  key={position.symbol}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="flex justify-between items-center p-2 rounded bg-dark-800/30 hover:bg-dark-800/50 transition-colors"
                >
                  <div>
                    <div className="text-sm font-medium text-white">{position.symbol}</div>
                    <div className="text-xs text-gray-400">{position.quantity.toFixed(2)}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-mono text-white">{formatPrice(position.marketValue)}</div>
                    {formatChange(position.dayReturn, position.dayReturnPercent)}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Recent Orders */}
          <div className="trading-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Recent orders</h3>
              <button className="text-primary-400 hover:text-primary-300 text-sm">
                View all
              </button>
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {recentOrders.map((order, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="flex justify-between items-center p-2 rounded bg-dark-800/30"
                >
                  <div>
                    <div className="text-sm font-medium text-white">{order.symbol}</div>
                    <div className="text-xs text-gray-400">{order.type}</div>
                  </div>
                  <div className="text-right">
                    <div className={`text-xs px-2 py-1 rounded ${
                      order.status === 'Working' ? 'bg-warning-600/20 text-warning-400' :
                      order.status === 'Filled' ? 'bg-success-600/20 text-success-400' :
                      'bg-gray-600/20 text-gray-400'
                    }`}>
                      {order.status}
                    </div>
                    <div className={`text-xs mt-1 ${
                      order.side === 'Buy' ? 'text-success-400' : 'text-danger-400'
                    }`}>
                      {order.side}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingDashboard;
