import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  CpuChipIcon,
  ChartBarIcon,
  BrainIcon,
  DatabaseIcon,
  DocumentTextIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import Card from '@/components/ui/Card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import apiClient from '@/api/client'

interface WorkflowStage {
  id: string
  name: string
  description: string
  icon: React.ComponentType<any>
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  duration?: number
  error?: string
}

interface WorkflowResult {
  workflow_id: string
  status: string
  current_stage: string
  stages_completed: string[]
  errors: string[]
  started_at: string
  completed_at?: string
  duration?: number
  results_summary: Record<string, boolean>
}

const WORKFLOW_STAGES: Record<string, { name: string; description: string; icon: React.ComponentType<any> }> = {
  initialization: {
    name: 'Initialization',
    description: 'Setting up workflow parameters',
    icon: PlayIcon
  },
  data_collection: {
    name: 'Data Collection',
    description: 'Gathering market data from multiple sources',
    icon: DatabaseIcon
  },
  data_validation: {
    name: 'Data Validation',
    description: 'Validating data quality and completeness',
    icon: CheckCircleIcon
  },
  correlation_analysis: {
    name: 'Correlation Analysis',
    description: 'Computing asset correlation matrices',
    icon: ChartBarIcon
  },
  ml_analysis: {
    name: 'ML Analysis',
    description: 'Training machine learning models',
    icon: BrainIcon
  },
  regime_detection: {
    name: 'Regime Detection',
    description: 'Identifying market regime patterns',
    icon: CpuChipIcon
  },
  network_analysis: {
    name: 'Network Analysis',
    description: 'Building correlation networks',
    icon: ChartBarIcon
  },
  llm_processing: {
    name: 'LLM Processing',
    description: 'Generating AI-powered insights',
    icon: BrainIcon
  },
  vector_storage: {
    name: 'Vector Storage',
    description: 'Storing embeddings in vector database',
    icon: DatabaseIcon
  },
  recommendation: {
    name: 'Recommendations',
    description: 'Generating investment recommendations',
    icon: DocumentTextIcon
  },
  reporting: {
    name: 'Report Generation',
    description: 'Creating comprehensive reports',
    icon: DocumentTextIcon
  },
  frontend_update: {
    name: 'Frontend Update',
    description: 'Updating dashboard with results',
    icon: ArrowPathIcon
  }
}

const WorkflowDashboard: React.FC = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [workflowSymbols, setWorkflowSymbols] = useState(['AAPL', 'MSFT', 'GOOGL'])
  const [workflowType, setWorkflowType] = useState('full_analysis')

  const queryClient = useQueryClient()

  // Fetch workflow list
  const { data: workflowList, isLoading: listLoading } = useQuery({
    queryKey: ['workflows'],
    queryFn: () => apiClient.request({ method: 'GET', url: '/workflow/list' }),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Fetch specific workflow status
  const { data: workflowStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['workflow-status', selectedWorkflow],
    queryFn: () => selectedWorkflow 
      ? apiClient.request({ method: 'GET', url: `/workflow/${selectedWorkflow}/status` })
      : null,
    enabled: !!selectedWorkflow,
    refetchInterval: 2000, // Refresh every 2 seconds for active workflows
  })

  // Start workflow mutation
  const startWorkflowMutation = useMutation({
    mutationFn: (params: { symbols: string[], workflow_type: string }) =>
      apiClient.request({
        method: 'POST',
        url: '/workflow/start',
        data: params,
      }),
    onSuccess: (data) => {
      setSelectedWorkflow(data.workflow_id)
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
    },
  })

  // Demo workflow mutation
  const demoWorkflowMutation = useMutation({
    mutationFn: () =>
      apiClient.request({
        method: 'POST',
        url: '/demo/full-workflow',
      }),
    onSuccess: (data) => {
      setSelectedWorkflow(data.workflow_id)
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
    },
  })

  const getStageStatus = (stageId: string, workflow: WorkflowResult): 'pending' | 'running' | 'completed' | 'failed' | 'skipped' => {
    if (workflow.stages_completed.includes(stageId)) {
      return 'completed'
    }
    if (workflow.current_stage === stageId && workflow.status === 'running') {
      return 'running'
    }
    if (workflow.errors.some(error => error.includes(stageId))) {
      return 'failed'
    }
    if (workflow.results_summary[stageId] === false) {
      return 'skipped'
    }
    return 'pending'
  }

  const getStageIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-6 h-6 text-green-500" />
      case 'running':
        return <ArrowPathIcon className="w-6 h-6 text-blue-500 animate-spin" />
      case 'failed':
        return <XCircleIcon className="w-6 h-6 text-red-500" />
      case 'skipped':
        return <ClockIcon className="w-6 h-6 text-yellow-500" />
      default:
        return <ClockIcon className="w-6 h-6 text-gray-400" />
    }
  }

  const renderWorkflowVisualization = (workflow: WorkflowResult) => {
    const stages = Object.entries(WORKFLOW_STAGES).map(([id, config]) => ({
      id,
      ...config,
      status: getStageStatus(id, workflow),
    }))

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stages.map((stage, index) => (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                stage.status === 'completed'
                  ? 'border-green-200 bg-green-50'
                  : stage.status === 'running'
                  ? 'border-blue-200 bg-blue-50'
                  : stage.status === 'failed'
                  ? 'border-red-200 bg-red-50'
                  : stage.status === 'skipped'
                  ? 'border-yellow-200 bg-yellow-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {getStageIcon(stage.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {stage.name}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {stage.description}
                  </p>
                  <div className="mt-2">
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        stage.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : stage.status === 'running'
                          ? 'bg-blue-100 text-blue-800'
                          : stage.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : stage.status === 'skipped'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {stage.status}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Workflow Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Monitor and manage comprehensive analysis workflows
        </p>
      </div>

      {/* Workflow Controls */}
      <Card title="Start New Workflow" subtitle="Configure and launch a new analysis workflow">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbols
              </label>
              <input
                type="text"
                value={workflowSymbols.join(', ')}
                onChange={(e) => setWorkflowSymbols(e.target.value.split(',').map(s => s.trim()))}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="AAPL, MSFT, GOOGL"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Workflow Type
              </label>
              <select
                value={workflowType}
                onChange={(e) => setWorkflowType(e.target.value)}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="full_analysis">Full Analysis</option>
                <option value="quick_analysis">Quick Analysis</option>
                <option value="ml_focused">ML Focused</option>
              </select>
            </div>
            <div className="flex items-end space-x-2">
              <button
                onClick={() => startWorkflowMutation.mutate({
                  symbols: workflowSymbols,
                  workflow_type: workflowType
                })}
                disabled={startWorkflowMutation.isPending}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {startWorkflowMutation.isPending ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  'Start Workflow'
                )}
              </button>
              <button
                onClick={() => demoWorkflowMutation.mutate()}
                disabled={demoWorkflowMutation.isPending}
                className="bg-green-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-green-700 disabled:opacity-50"
              >
                Demo
              </button>
            </div>
          </div>
        </div>
      </Card>

      {/* Active Workflows */}
      <Card title="Active Workflows" subtitle="Current and recent workflow executions">
        {listLoading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : workflowList?.workflows?.length > 0 ? (
          <div className="space-y-4">
            {workflowList.workflows.map((workflow: any) => (
              <div
                key={workflow.workflow_id}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  selectedWorkflow === workflow.workflow_id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedWorkflow(workflow.workflow_id)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {workflow.workflow_id}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Status: {workflow.status} • Stage: {workflow.current_stage}
                    </p>
                    <p className="text-xs text-gray-400">
                      Started: {new Date(workflow.started_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <div
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        workflow.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : workflow.status === 'running'
                          ? 'bg-blue-100 text-blue-800'
                          : workflow.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {workflow.status}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {workflow.stages_completed}/{Object.keys(WORKFLOW_STAGES).length} stages
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No workflows found. Start a new workflow to begin.
          </div>
        )}
      </Card>

      {/* Workflow Visualization */}
      {selectedWorkflow && workflowStatus && (
        <Card
          title={`Workflow: ${selectedWorkflow}`}
          subtitle={`Status: ${workflowStatus.status} • Current Stage: ${workflowStatus.current_stage}`}
        >
          {statusLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="space-y-6">
              {/* Workflow Progress */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Progress</span>
                  <span className="text-sm text-gray-500">
                    {workflowStatus.stages_completed.length}/{Object.keys(WORKFLOW_STAGES).length} stages
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${(workflowStatus.stages_completed.length / Object.keys(WORKFLOW_STAGES).length) * 100}%`
                    }}
                  />
                </div>
              </div>

              {/* Stage Visualization */}
              {renderWorkflowVisualization(workflowStatus)}

              {/* Errors */}
              {workflowStatus.errors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-red-800 mb-2">Errors</h4>
                  <ul className="space-y-1">
                    {workflowStatus.errors.map((error, index) => (
                      <li key={index} className="text-sm text-red-700">
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Workflow Metadata */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-gray-500">Started At</p>
                  <p className="text-sm font-medium">
                    {new Date(workflowStatus.started_at).toLocaleString()}
                  </p>
                </div>
                {workflowStatus.completed_at && (
                  <div>
                    <p className="text-xs text-gray-500">Completed At</p>
                    <p className="text-sm font-medium">
                      {new Date(workflowStatus.completed_at).toLocaleString()}
                    </p>
                  </div>
                )}
                {workflowStatus.duration && (
                  <div>
                    <p className="text-xs text-gray-500">Duration</p>
                    <p className="text-sm font-medium">
                      {Math.round(workflowStatus.duration)}s
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-xs text-gray-500">Stages Completed</p>
                  <p className="text-sm font-medium">
                    {workflowStatus.stages_completed.length}
                  </p>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}

export default WorkflowDashboard
