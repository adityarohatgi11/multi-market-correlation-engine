import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import apiClient from '@/api/client'
import type { VectorPattern } from '@/types'
import Card from '@/components/ui/Card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { toast } from 'react-hot-toast'

const VectorSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPatternType, setSelectedPatternType] = useState<string>('all')
  const [searchResults, setSearchResults] = useState<VectorPattern[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Query vector database stats
  const { data: vectorStats } = useQuery({
    queryKey: ['vector-stats'],
    queryFn: () => apiClient.getVectorStats(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query')
      return
    }

    setIsSearching(true)
    try {
      const results = await apiClient.searchVectorPatterns({
        query: searchQuery,
        k: 10,
        pattern_type: selectedPatternType === 'all' ? undefined : selectedPatternType,
      })
      
      setSearchResults(results)
      toast.success(`Found ${results.length} matching patterns`)
    } catch (error) {
      console.error('Search error:', error)
      toast.error('Failed to search vector database')
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const patternTypes = ['all', 'bullish', 'bearish', 'consolidation', 'breakout', 'reversal']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vector Search</h1>
          <p className="text-gray-600">FAISS semantic pattern matching for market analysis</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-blue-600 mr-3" />
            <div>
              <p className="text-sm text-gray-500">Total Patterns</p>
              <p className="text-2xl font-bold text-gray-900">
                {vectorStats?.total_patterns.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center">
            <FunnelIcon className="h-8 w-8 text-purple-600 mr-3" />
            <div>
              <p className="text-sm text-gray-500">Index Type</p>
              <p className="text-2xl font-bold text-gray-900">
                {vectorStats?.index_type || 'N/A'}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <p className="text-sm text-gray-500">Dimensions</p>
              <p className="text-2xl font-bold text-gray-900">
                {vectorStats?.dimension || '0'}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Search Interface */}
      <Card>
        <div className="p-6">
          <form onSubmit={(e) => { e.preventDefault(); handleSearch() }} className="space-y-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Search for patterns, e.g., 'high volatility tech stocks', 'bull market correlations'..."
                  className="input w-full"
                />
              </div>
              <select
                value={selectedPatternType}
                onChange={(e) => setSelectedPatternType(e.target.value)}
                className="input w-48"
              >
                {patternTypes.map((type) => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
              <button
                type="submit"
                disabled={!searchQuery.trim() || isSearching}
                className="btn-primary px-6"
              >
                {isSearching ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
                    Search
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </Card>

      {/* Search Results */}
      {isSearching && (
        <Card>
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" text="Searching vector database..." />
          </div>
        </Card>
      )}

      {searchResults.length > 0 && (
        <Card title="Search Results" subtitle={`Found ${searchResults.length} matching patterns`}>
          <div className="divide-y divide-gray-200">
            {searchResults.map((pattern, index) => (
              <motion.div
                key={pattern.pattern_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">
                        {pattern.symbol}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        pattern.pattern_type === 'bullish' ? 'bg-green-100 text-green-800' :
                        pattern.pattern_type === 'bearish' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {pattern.pattern_type}
                      </span>
                      <span className="text-sm text-gray-500">
                        ID: {pattern.pattern_id}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Similarity:</span>
                        <span className="ml-1 font-medium">
                          {((pattern.similarity_score || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Distance:</span>
                        <span className="ml-1 font-medium">
                          {(pattern.distance || 0).toFixed(4)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Timestamp:</span>
                        <span className="ml-1 font-medium">
                          {new Date(pattern.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Type:</span>
                        <span className="ml-1 font-medium">{pattern.pattern_type}</span>
                      </div>
                    </div>

                    {pattern.metadata && Object.keys(pattern.metadata).length > 0 && (
                      <div className="mt-3">
                        <details className="group">
                          <summary className="cursor-pointer text-sm text-primary-600 hover:text-primary-700">
                            View metadata ({Object.keys(pattern.metadata).length} fields)
                          </summary>
                          <div className="mt-2 p-3 bg-gray-50 rounded-md">
                            <pre className="text-xs text-gray-600 overflow-x-auto">
                              {JSON.stringify(pattern.metadata, null, 2)}
                            </pre>
                          </div>
                        </details>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Empty State */}
      {!isSearching && searchResults.length === 0 && searchQuery && (
        <Card>
          <div className="text-center py-12">
            <MagnifyingGlassIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No patterns found</h3>
            <p className="text-gray-500 mb-4">
              No patterns match your search query. Try different keywords or pattern types.
            </p>
            <button
              onClick={() => setSearchQuery('')}
              className="btn-secondary"
            >
              Clear search
            </button>
          </div>
        </Card>
      )}

      {/* Pattern Distribution */}
      {vectorStats?.pattern_types && (
        <Card title="Pattern Distribution" subtitle="Distribution of pattern types in the database">
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {Object.entries(vectorStats.pattern_types).map(([type, count]) => (
                <div key={type} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{count as React.ReactNode}</div>
                  <div className="text-sm text-gray-500 capitalize">{type}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default VectorSearch 