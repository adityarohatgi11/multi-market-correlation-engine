import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  PaperAirplaneIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  SparklesIcon,
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
      const response = await apiClient.sendChatMessage({ 
        message: inputMessage,
        context: { conversation_id: Date.now().toString() }
      })

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content || 'I received your message but had trouble processing it.',
        timestamp: new Date().toISOString(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message to LLM')
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const suggestedQuestions = [
    "What are the current market correlations?",
    "Analyze the risk profile of my portfolio",
    "What trading opportunities do you see?",
    "Explain the latest market trends",
  ]

  const handleSuggestedQuestion = (question: string) => {
    setInputMessage(question)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">LLM Assistant</h1>
          <p className="text-gray-600">AI-powered financial insights and analysis</p>
        </div>
        <div className="flex items-center space-x-4">
          {llmStatus && (
            <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
              llmStatus.model_available 
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                llmStatus.model_available ? 'bg-green-500' : 'bg-red-500'
              }`} />
              {llmStatus.model_available ? 'Model Available' : 'Model Loading'}
            </div>
          )}
        </div>
      </div>

      {/* Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Chat */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center">
                <ChatBubbleLeftRightIcon className="w-5 h-5 text-primary-600 mr-2" />
                <h3 className="text-lg font-medium text-gray-900">Chat Assistant</h3>
              </div>
              <div className="text-sm text-gray-500">
                {llmStatus?.model_available ? 'Ready' : 'Loading...'}
              </div>
            </div>

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
                    {suggestedQuestions.map((question) => (
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

            {/* Message Input */}
            <div className="p-4 border-t border-gray-200">
              <form onSubmit={(e) => { e.preventDefault(); handleSendMessage() }} className="flex space-x-3">
                <div className="flex-1">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder={
                      llmStatus?.model_available 
                        ? "Ask me about market analysis, correlations, or portfolio strategies..."
                        : "LLM model is loading, please wait..."
                    }
                    disabled={!llmStatus?.model_available || isLoading}
                    className="block w-full rounded-lg border border-gray-300 px-4 py-3 text-sm placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || !llmStatus?.model_available || isLoading}
                  className="btn-primary px-4 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <PaperAirplaneIcon className="w-5 h-5" />
                  )}
                </button>
              </form>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Model Status */}
          <Card title="Model Status" className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Model Status</span>
                <span className={`text-sm font-medium ${
                  llmStatus?.model_available ? 'text-green-600' : 'text-red-600'
                }`}>
                  {llmStatus?.model_available ? 'Available' : 'Loading'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Chat Messages</span>
                <span className="text-sm font-medium text-gray-900">
                  {messages.length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Vector Patterns</span>
                <span className="text-sm font-medium text-gray-900">
                  {llmStatus?.vector_patterns || 0}
                </span>
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <Card title="Quick Analysis" className="p-4">
            <div className="space-y-2">
              {[
                "Generate market report",
                "Analyze portfolio risk",
                "Explain correlations",
                "Suggest optimizations"
              ].map((action) => (
                <button
                  key={action}
                  onClick={() => handleSuggestedQuestion(action)}
                  className="w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded transition-colors"
                >
                  <SparklesIcon className="w-4 h-4 inline mr-2" />
                  {action}
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default LLMAssistant
