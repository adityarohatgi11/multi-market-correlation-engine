import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  BoltIcon,
  CloudArrowDownIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'
import Card from '@/components/ui/Card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { toast } from 'react-hot-toast'

interface WorkflowStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  duration?: string
  output?: string
  error?: string
}

interface WorkflowRun {
  id: string
  name: string
  status: 'idle' | 'running' | 'completed' | 'failed'
  startTime?: string
  endTime?: string
  duration?: string
  steps: WorkflowStep[]
  totalSteps: number
  completedSteps: number
}

const WorkflowDashboard: React.FC = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>('etl_pipeline')
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true)
  const queryClient = useQueryClient()

  // Mock workflow data - in production this would come from your backend
  const workflows: WorkflowRun[] = [
    {
      id: 'etl_pipeline',
      name: 'ETL Data Pipeline',
      status: 'idle',
      totalSteps: 7,
      completedSteps: 7,
      duration: '18m 32s',
      endTime: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      steps: [
        { id: 'health_check', name: 'Data Source Health Check', status: 'completed', duration: '2s' },
        { id: 'yahoo_finance', name: 'Yahoo Finance Collection', status: 'completed', duration: '8m 15s' },
        { id: 'fred_data', name: 'FRED Economic Data', status: 'completed', duration: '3m 45s' },
        { id: 'validation', name: 'Data Validation & Quality Check', status: 'completed', duration: '1m 30s' },
        { id: 'database_storage', name: 'Database Storage', status: 'completed', duration: '2m 20s' },
        { id: 'index_update', name: 'Index Updating', status: 'completed', duration: '1m 45s' },
        { id: 'cache_refresh', name: 'Cache Refresh', status: 'completed', duration: '58s' }
      ]
    },
    {
      id: 'correlation_analysis',
      name: 'Correlation Analysis',
      status: 'completed',
      totalSteps: 5,
      completedSteps: 5,
      duration: '5m 12s',
      endTime: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      steps: [
        { id: 'data_preparation', name: 'Data Preparation', status: 'completed', duration: '45s' },
        { id: 'correlation_calculation', name: 'Correlation Calculation', status: 'completed', duration: '2m 30s' },
        { id: 'statistical_tests', name: 'Statistical Significance Tests', status: 'completed', duration: '1m 15s' },
        { id: 'visualization', name: 'Visualization Generation', status: 'completed', duration: '25s' },
        { id: 'report_generation', name: 'Report Generation', status: 'completed', duration: '17s' }
      ]
    },
    {
      id: 'risk_assessment',
      name: 'Portfolio Risk Assessment',
      status: 'failed',
      totalSteps: 4,
      completedSteps: 2,
      duration: '2m 45s',
      endTime: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      steps: [
        { id: 'portfolio_data', name: 'Portfolio Data Loading', status: 'completed', duration: '15s' },
        { id: 'var_calculation', name: 'VaR Calculation', status: 'completed', duration: '1m 30s' },
        { id: 'stress_testing', name: 'Stress Testing', status: 'failed', duration: '1m', error: 'Market scenario data unavailable' },
        { id: 'risk_report', name: 'Risk Report Generation', status: 'pending' }
      ]
    },
    {
      id: 'ml_model_training',
      name: 'ML Model Training',
      status: 'running',
      totalSteps: 6,
      completedSteps: 3,
      startTime: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      steps: [
        { id: 'feature_engineering', name: 'Feature Engineering', status: 'completed', duration: '3m 20s' },
        { id: 'data_splitting', name: 'Train/Test Split', status: 'completed', duration: '45s' },
        { id: 'model_training', name: 'Model Training', status: 'completed', duration: '8m 15s' },
        { id: 'hyperparameter_tuning', name: 'Hyperparameter Tuning', status: 'running' },
        { id: 'model_validation', name: 'Model Validation', status: 'pending' },
        { id: 'model_deployment', name: 'Model Deployment', status: 'pending' }
      ]
    }
  ]

  // Simulate API calls for workflow management
  const triggerETL = useMutation({
    mutationFn: async () => {
      const response = await fetch('http://localhost:8000/etl/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      return response.json()
    },
    onSuccess: (data) => {
      toast.success('ETL Pipeline triggered successfully')
      queryClient.invalidateQueries({ queryKey: ['etl-status'] })
    },
    onError: (error) => {
      toast.error('Failed to trigger ETL pipeline')
      console.error('ETL trigger error:', error)
    }
  })

  const triggerCorrelationAnalysis = useMutation({
    mutationFn: async () => {
      const response = await fetch('http://localhost:8000/analysis/correlation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      return response.json()
    },
    onSuccess: () => {
      toast.success('Correlation analysis started')
    },
    onError: () => {
      toast.error('Failed to start correlation analysis')
    }
  })

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      // In production, this would fetch real-time workflow status
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
    }, 5000)

    return () => clearInterval(interval)
  }, [autoRefresh, queryClient])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'running':
        return 'text-blue-600 bg-blue-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      case 'pending':
        return 'text-gray-600 bg-gray-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4" />
      case 'running':
        return <ArrowPathIcon className="w-4 h-4 animate-spin" />
      case 'failed':
        return <ExclamationCircleIcon className="w-4 h-4" />
      case 'pending':
        return <ClockIcon className="w-4 h-4" />
      default:
        return <ClockIcon className="w-4 h-4" />
    }
  }

  const selectedWorkflowData = workflows.find(w => w.id === selectedWorkflow)

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflow Dashboard</h1>
          <p className="text-gray-600">Monitor and manage automated workflows and processes</p>
        </div>
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="ml-2 text-sm text-gray-600">Auto-refresh</span>
          </label>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['workflows'] })}
            className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <ArrowPathIcon className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">ETL Pipeline</h3>
              <p className="text-xs text-gray-500">Data collection & processing</p>
            </div>
            <button
              onClick={() => triggerETL.mutate()}
              disabled={triggerETL.isPending}
              className="flex items-center px-3 py-1 bg-primary-600 text-white rounded text-sm hover:bg-primary-700 disabled:opacity-50"
            >
              <CloudArrowDownIcon className="w-4 h-4 mr-1" />
              {triggerETL.isPending ? 'Starting...' : 'Run ETL'}
            </button>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Correlation Analysis</h3>
              <p className="text-xs text-gray-500">Market correlation analysis</p>
            </div>
            <button
              onClick={() => triggerCorrelationAnalysis.mutate()}
              disabled={triggerCorrelationAnalysis.isPending}
              className="flex items-center px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50"
            >
              <ChartBarIcon className="w-4 h-4 mr-1" />
              {triggerCorrelationAnalysis.isPending ? 'Starting...' : 'Analyze'}
            </button>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Model Training</h3>
              <p className="text-xs text-gray-500">ML model retraining</p>
            </div>
            <button
              className="flex items-center px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
            >
              <CpuChipIcon className="w-4 h-4 mr-1" />
              Train
            </button>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Risk Assessment</h3>
              <p className="text-xs text-gray-500">Portfolio risk calculation</p>
            </div>
            <button
              className="flex items-center px-3 py-1 bg-orange-600 text-white rounded text-sm hover:bg-orange-700"
            >
              <BoltIcon className="w-4 h-4 mr-1" />
              Assess
            </button>
          </div>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workflow List */}
        <div className="lg:col-span-1">
          <Card>
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Active Workflows</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {workflows.map((workflow) => (
                <button
                  key={workflow.id}
                  onClick={() => setSelectedWorkflow(workflow.id)}
                  className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                    selectedWorkflow === workflow.id ? 'bg-primary-50 border-r-2 border-primary-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900">{workflow.name}</h4>
                      <div className="flex items-center mt-1">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(workflow.status)}`}>
                          {getStatusIcon(workflow.status)}
                          <span className="ml-1 capitalize">{workflow.status}</span>
                        </span>
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        {workflow.completedSteps}/{workflow.totalSteps} steps
                        {workflow.duration && ` • ${workflow.duration}`}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* Workflow Details */}
        <div className="lg:col-span-2">
          <Card>
            <div className="p-6">
              {selectedWorkflowData ? (
                <div>
                  {/* Workflow Header */}
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{selectedWorkflowData.name}</h3>
                      <div className="flex items-center mt-2 space-x-4">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedWorkflowData.status)}`}>
                          {getStatusIcon(selectedWorkflowData.status)}
                          <span className="ml-2 capitalize">{selectedWorkflowData.status}</span>
                        </span>
                        {selectedWorkflowData.duration && (
                          <span className="text-sm text-gray-500">
                            Duration: {selectedWorkflowData.duration}
                          </span>
                        )}
                        {selectedWorkflowData.endTime && (
                          <span className="text-sm text-gray-500">
                            Completed: {new Date(selectedWorkflowData.endTime).toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      {selectedWorkflowData.status === 'running' && (
                        <button className="flex items-center px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                          <StopIcon className="w-4 h-4 mr-2" />
                          Stop
                        </button>
                      )}
                      {selectedWorkflowData.status !== 'running' && (
                        <button className="flex items-center px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                          <PlayIcon className="w-4 h-4 mr-2" />
                          Restart
                        </button>
                      )}
                      <button className="flex items-center px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                        <Cog6ToothIcon className="w-4 h-4 mr-2" />
                        Configure
                      </button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">Progress</span>
                      <span className="text-sm text-gray-500">
                        {selectedWorkflowData.completedSteps}/{selectedWorkflowData.totalSteps} steps
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${(selectedWorkflowData.completedSteps / selectedWorkflowData.totalSteps) * 100}%`
                        }}
                      />
                    </div>
                  </div>

                  {/* Workflow Steps */}
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-4">Workflow Steps</h4>
                    <div className="space-y-4">
                      {selectedWorkflowData.steps.map((step, index) => (
                        <motion.div
                          key={step.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`border rounded-lg p-4 ${
                            step.status === 'running' ? 'border-blue-300 bg-blue-50' : 'border-gray-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <span className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${getStatusColor(step.status)}`}>
                                {step.status === 'running' ? (
                                  <ArrowPathIcon className="w-4 h-4 animate-spin" />
                                ) : (
                                  index + 1
                                )}
                              </span>
                              <div className="ml-4">
                                <h5 className="text-sm font-medium text-gray-900">{step.name}</h5>
                                {step.error && (
                                  <p className="text-sm text-red-600 mt-1">{step.error}</p>
                                )}
                                {step.output && (
                                  <p className="text-sm text-gray-600 mt-1">{step.output}</p>
                                )}
                              </div>
                            </div>
                            <div className="text-right">
                              {step.duration && (
                                <span className="text-sm text-gray-500">{step.duration}</span>
                              )}
                              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ml-2 ${getStatusColor(step.status)}`}>
                                {getStatusIcon(step.status)}
                                <span className="ml-1 capitalize">{step.status}</span>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <DocumentTextIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Workflow Selected</h3>
                  <p className="text-gray-500">Select a workflow from the list to view details</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Recent Activity */}
      <Card>
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            {workflows.map((workflow) => (
              <div key={`activity-${workflow.id}`} className="flex items-center justify-between py-2">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${
                    workflow.status === 'completed' ? 'bg-green-500' :
                    workflow.status === 'running' ? 'bg-blue-500' :
                    workflow.status === 'failed' ? 'bg-red-500' : 'bg-gray-500'
                  }`} />
                  <span className="text-sm text-gray-900">{workflow.name}</span>
                  <span className={`ml-2 text-xs font-medium ${getStatusColor(workflow.status)} px-2 py-1 rounded-full`}>
                    {workflow.status}
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  {workflow.endTime ? (
                    <>Completed {new Date(workflow.endTime).toLocaleDateString()}</>
                  ) : workflow.startTime ? (
                    <>Started {new Date(workflow.startTime).toLocaleTimeString()}</>
                  ) : (
                    'Scheduled'
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  )
}

export default WorkflowDashboard
