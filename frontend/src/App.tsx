import { FC } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/layout/Layout'
import Dashboard from '@/pages/Dashboard'
import WorkflowDashboard from '@/pages/WorkflowDashboard'
import LLMAssistant from '@/pages/LLMAssistant'
import VectorSearch from '@/pages/VectorSearch'
import MarketAnalysis from '@/pages/MarketAnalysis'
import Portfolio from '@/pages/Portfolio'
import Reports from '@/pages/Reports'
import Settings from '@/pages/Settings'

const App: FC = () => {
  return (
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
        </Routes>
      </Layout>
    </div>
  )
}

export default App 