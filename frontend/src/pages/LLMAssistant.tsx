import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  PaperAirplaneIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  SparklesIcon,
  MagnifyingGlassIcon,
  BeakerIcon,
  CircleStackIcon
} from '@heroicons/react/24/outline'
import apiClient from '@/api/client'
import type { ChatMessage } from '@/types'
import Card from '@/components/ui/Card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ReactMarkdown from 'react-markdown'
import { toast } from 'react-hot-toast'

const LLMAssistant: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'vector' | 'analysis'>('chat')
  const [vectorQuery, setVectorQuery] = useState('')
  const [vectorResults, setVectorResults] = useState<any[]>([])
  const [vectorLoading, setVectorLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Query LLM status
  const { data: llmStatus } = useQuery({
    queryKey: ['llm-status'],
    queryFn: () => apiClient.getLLMStatus(),
    refetchInterval: 10000, // Check every 10 seconds
  })

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Use the simplified chat endpoint
      const response = await fetch('http://localhost:8000/llm/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          user_id: 'frontend_user'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.data?.response || 'I received your message but had trouble processing it.',
        timestamp: new Date().toISOString(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message to LLM')
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. The LLM service might be starting up. Please try again in a moment.',
        timestamp: new Date().toISOString(),
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleVectorSearch = async () => {
    if (!vectorQuery.trim() || vectorLoading) return

    setVectorLoading(true)
    try {
      const response = await fetch('http://localhost:8000/llm/vector/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_type: 'text',
          query_data: vectorQuery,
          k: 5
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      setVectorResults(data.data?.results || [])
      toast.success(`Found ${data.data?.count || 0} similar patterns`)
    } catch (error) {
      console.error('Error in vector search:', error)
      toast.error('Vector search failed')
      setVectorResults([])
    } finally {
      setVectorLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (activeTab === 'chat') {
        handleSendMessage()
      } else if (activeTab === 'vector') {
        handleVectorSearch()
      }
    }
  }

  const suggestedQuestions = [
    "What are the current market correlations?",
    "Analyze the risk profile of my portfolio", 
    "What trading opportunities do you see?",
    "Explain the latest market trends",
    "Search for high volatility tech stocks",
    "Find similar patterns to Apple's recent performance"
  ]

  const vectorSuggestions = [
    "high volatility tech stocks",
    "stable dividend income investments",
    "growth momentum patterns",
    "market crash indicators",
    "correlation breakdowns"
  ]

  const handleSuggestedQuestion = (question: string) => {
    if (activeTab === 'chat') {
      setInputMessage(question)
    } else if (activeTab === 'vector') {
      setVectorQuery(question)
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'chat':
        return renderChatTab()
      case 'vector':
        return renderVectorTab()
      case 'analysis':
        return renderAnalysisTab()
      default:
        return renderChatTab()
    }
  }

  const renderChatTab = () => (
    <div className="h-[600px] flex flex-col">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <ChatBubbleLeftRightIcon className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to your AI Assistant
            </h3>
            <p className="text-gray-500 mb-6 max-w-md">
              Ask me about market analysis, portfolio optimization, risk assessment, 
              or any financial questions you have.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg">
              {suggestedQuestions.slice(0, 4).map((question) => (
                <button
                  key={question}
                  onClick={() => handleSuggestedQuestion(question)}
                  className="text-left p-3 text-sm text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <div className="prose prose-sm max-w-none">
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                </div>
                <div className={`text-xs mt-2 ${
                  msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  <ClockIcon className="w-3 h-3 inline mr-1" />
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </motion.div>
          ))
        )}
        
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <LoadingSpinner size="sm" text="Thinking..." />
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-4">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about markets and finance..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )

  const renderVectorTab = () => (
    <div className="h-[600px] flex flex-col">
      {/* Vector Search Input */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex space-x-4">
          <input
            type="text"
            value={vectorQuery}
            onChange={(e) => setVectorQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search for financial patterns, e.g., 'high volatility tech stocks'"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={vectorLoading}
          />
          <button
            onClick={handleVectorSearch}
            disabled={vectorLoading || !vectorQuery.trim()}
            className="flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <MagnifyingGlassIcon className="w-5 h-5" />
          </button>
        </div>
        
        {/* Vector Search Suggestions */}
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-2">Try searching for:</p>
          <div className="flex flex-wrap gap-2">
            {vectorSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setVectorQuery(suggestion)}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Vector Search Results */}
      <div className="flex-1 overflow-y-auto p-4">
        {vectorLoading ? (
          <div className="flex items-center justify-center h-full">
            <LoadingSpinner text="Searching vector database..." />
          </div>
        ) : vectorResults.length > 0 ? (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">
              Found {vectorResults.length} Similar Patterns
            </h3>
            {vectorResults.map((result, index) => (
              <motion.div
                key={result.pattern_id || index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">
                      {result.symbol} - {result.pattern_type}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {result.description}
                    </p>
                    <div className="flex items-center mt-2 space-x-4">
                      <span className="text-sm font-medium text-primary-600">
                        Similarity: {(result.similarity_score * 100).toFixed(1)}%
                      </span>
                      {result.metadata?.sector && (
                        <span className="text-sm text-gray-500">
                          Sector: {result.metadata.sector}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <CircleStackIcon className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : vectorQuery ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <MagnifyingGlassIcon className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No patterns found</h3>
            <p className="text-gray-500">Try a different search query or check your spelling.</p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <CircleStackIcon className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Vector Pattern Search</h3>
            <p className="text-gray-500 mb-4">
              Search for similar financial patterns using AI-powered semantic matching.
            </p>
          </div>
        )}
      </div>
    </div>
  )

  const renderAnalysisTab = () => (
    <div className="h-[600px] flex flex-col">
      <div className="flex-1 p-4">
        <div className="text-center py-16">
          <BeakerIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Advanced Analysis</h3>
          <p className="text-gray-500">
            Advanced market analysis tools will be available here.
          </p>
        </div>
      </div>
    </div>
  )

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">LLM Assistant</h1>
          <p className="text-gray-600">AI-powered financial insights, chat, and vector search</p>
        </div>
        <div className="flex items-center space-x-4">
          {llmStatus && (
            <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
              llmStatus.model_available 
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                llmStatus.model_available ? 'bg-green-500' : 'bg-yellow-500'
              }`} />
              {llmStatus.model_available ? 'Model Ready' : 'Demo Mode'}
            </div>
          )}
        </div>
      </div>

      {/* Tabs and Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3">
          <Card>
            {/* Tab Navigation */}
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setActiveTab('chat')}
                className={`flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'chat'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <ChatBubbleLeftRightIcon className="w-4 h-4 mr-2" />
                Chat Assistant
              </button>
              <button
                onClick={() => setActiveTab('vector')}
                className={`flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'vector'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <MagnifyingGlassIcon className="w-4 h-4 mr-2" />
                Vector Search
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'analysis'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <BeakerIcon className="w-4 h-4 mr-2" />
                Analysis
              </button>
            </div>

            {/* Tab Content */}
            {renderTabContent()}
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Model Status */}
          <Card>
            <div className="p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Model Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">LLM Model</span>
                  <span className={`text-sm font-medium ${
                    llmStatus?.model_available ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {llmStatus?.model_available ? 'Ready' : 'Demo Mode'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Vector Database</span>
                  <span className="text-sm font-medium text-blue-600">
                    {llmStatus?.vector_patterns || 0} patterns
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Chat Messages</span>
                  <span className="text-sm font-medium text-gray-900">
                    {messages.length}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <Card>
            <div className="p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={() => handleSuggestedQuestion("What are the current market correlations?")}
                  className="w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded transition-colors"
                >
                  Market Correlations
                </button>
                <button
                  onClick={() => handleSuggestedQuestion("high volatility tech stocks")}
                  className="w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded transition-colors"
                >
                  Find Tech Patterns
                </button>
                <button
                  onClick={() => handleSuggestedQuestion("Analyze portfolio risk")}
                  className="w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded transition-colors"
                >
                  Risk Analysis
                </button>
                <button
                  onClick={() => {
                    setMessages([])
                    setVectorResults([])
                    setVectorQuery('')
                    setInputMessage('')
                  }}
                  className="w-full text-left p-2 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
                >
                  Clear All
                </button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default LLMAssistant
