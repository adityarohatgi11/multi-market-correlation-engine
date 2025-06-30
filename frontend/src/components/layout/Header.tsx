import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Bars3Icon,
  BellIcon,
  UserCircleIcon,
  MagnifyingGlassIcon,
  CpuChipIcon,
  SignalIcon,
} from '@heroicons/react/24/outline'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'

interface HeaderProps {
  onMenuClick: () => void
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [showNotifications, setShowNotifications] = useState(false)

  // Health check query
  const { data: healthStatus } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
    retry: 1,
  })

  // LLM status query
  const { data: llmStatus } = useQuery({
    queryKey: ['llm-status'],
    queryFn: () => apiClient.getLLMStatus(),
    refetchInterval: 60000, // Check every minute
    retry: 1,
  })

  const isOnline = healthStatus?.status === 'ok'
  const llmAvailable = llmStatus?.model_available

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          {/* Page title and breadcrumb */}
          <div className="hidden lg:block">
            <h1 className="text-2xl font-bold text-gray-900">
              Multi-Market Correlation Engine
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Advanced Financial Analysis with AI-Powered Insights
            </p>
          </div>
        </div>

        {/* Center - Search bar */}
        <div className="flex-1 max-w-lg mx-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search symbols, patterns, or insights..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Status indicators */}
          <div className="hidden md:flex items-center space-x-3">
            {/* API Status */}
            <motion.div
              className="flex items-center space-x-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <div
                className={`w-2 h-2 rounded-full ${
                  isOnline ? 'bg-green-400' : 'bg-red-400'
                }`}
              />
              <span className="text-sm text-gray-600">
                API {isOnline ? 'Online' : 'Offline'}
              </span>
            </motion.div>

            {/* LLM Status */}
            <motion.div
              className="flex items-center space-x-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <CpuChipIcon
                className={`w-4 h-4 ${
                  llmAvailable ? 'text-green-500' : 'text-orange-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                LLM {llmAvailable ? 'Ready' : 'Loading'}
              </span>
            </motion.div>

            {/* Vector DB Status */}
            <motion.div
              className="flex items-center space-x-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <SignalIcon className="w-4 h-4 text-blue-500" />
              <span className="text-sm text-gray-600">
                FAISS {llmStatus?.vector_patterns || 0} patterns
              </span>
            </motion.div>
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-500 hover:bg-gray-100 relative"
            >
              <BellIcon className="h-6 w-6" />
              <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white" />
            </button>

            {/* Notifications dropdown */}
            {showNotifications && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
              >
                <div className="px-4 py-2 border-b border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900">Notifications</h3>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  <div className="px-4 py-3 hover:bg-gray-50">
                    <p className="text-sm text-gray-900">
                      New market correlation pattern detected
                    </p>
                    <p className="text-xs text-gray-500 mt-1">2 minutes ago</p>
                  </div>
                  <div className="px-4 py-3 hover:bg-gray-50">
                    <p className="text-sm text-gray-900">
                      Portfolio rebalancing recommendation available
                    </p>
                    <p className="text-xs text-gray-500 mt-1">15 minutes ago</p>
                  </div>
                  <div className="px-4 py-3 hover:bg-gray-50">
                    <p className="text-sm text-gray-900">
                      Vector database updated with new patterns
                    </p>
                    <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
                  </div>
                </div>
                <div className="px-4 py-2 border-t border-gray-200">
                  <button className="text-sm text-primary-600 hover:text-primary-700">
                    View all notifications
                  </button>
                </div>
              </motion.div>
            )}
          </div>

          {/* User menu */}
          <div className="relative">
            <button className="flex items-center space-x-2 p-2 rounded-lg text-gray-700 hover:bg-gray-100">
              <UserCircleIcon className="h-8 w-8" />
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium">Admin User</p>
                <p className="text-xs text-gray-500">admin@example.com</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile status bar */}
      <div className="lg:hidden mt-4 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'}`} />
            <span>API {isOnline ? 'Online' : 'Offline'}</span>
          </div>
          <div className="flex items-center space-x-1">
            <CpuChipIcon className={`w-3 h-3 ${llmAvailable ? 'text-green-500' : 'text-orange-500'}`} />
            <span>LLM {llmAvailable ? 'Ready' : 'Loading'}</span>
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <SignalIcon className="w-3 h-3 text-blue-500" />
          <span>FAISS {llmStatus?.vector_patterns || 0}</span>
        </div>
      </div>
    </header>
  )
}

export default Header 