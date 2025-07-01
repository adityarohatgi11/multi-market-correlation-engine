import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import WorkflowDashboard from './pages/WorkflowDashboard'
import MarketAnalysis from './pages/MarketAnalysis'
import LLMAssistant from './pages/LLMAssistant'
import VectorSearch from './pages/VectorSearch'
import Portfolio from './pages/Portfolio'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import TradingDashboard from './pages/TradingDashboard'
import Analysis from './pages/Analysis'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/workflow" element={<WorkflowDashboard />} />
              <Route path="/market-analysis" element={<MarketAnalysis />} />
              <Route path="/llm-assistant" element={<LLMAssistant />} />
              <Route path="/vector-search" element={<VectorSearch />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/trading" element={<TradingDashboard />} />
              <Route path="/analysis" element={<Analysis />} />
            </Routes>
          </Layout>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App 