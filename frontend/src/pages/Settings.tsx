import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Cog6ToothIcon,
  ChartBarIcon,
  CloudIcon,
  BellIcon,
  ShieldCheckIcon,
  ServerIcon,
  CpuChipIcon,
  ArrowPathIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import Card from '@/components/ui/Card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { toast } from 'react-hot-toast'

interface SettingsData {
  analysis_settings: {
    correlation_method: string
    rolling_window: number
    investment_horizon: string
    risk_tolerance: string
  }
  data_settings: {
    update_frequency: string
    api_rate_limit: string
    data_retention: string
    auto_etl: boolean
    etl_schedule: string
  }
  model_settings: {
    garch_order: number[]
    var_max_lags: number
    ml_lookback_period: number
    ensemble_models: boolean
  }
  notification_settings: {
    email_alerts: boolean
    slack_alerts: boolean
    alert_threshold: number
    daily_reports: boolean
  }
  performance_settings: {
    cache_enabled: boolean
    batch_size: number
    concurrent_requests: number
    timeout_seconds: number
  }
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('analysis')
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<boolean>(false)
  const [localSettings, setLocalSettings] = useState<SettingsData | null>(null)
  const queryClient = useQueryClient()

  // Fetch current settings
  const { data: settings, isLoading, error } = useQuery<SettingsData>({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/settings')
      if (!response.ok) {
        throw new Error('Failed to fetch settings')
      }
      return response.json()
    },
  })

  // Update settings mutation
  const updateSettingsMutation = useMutation({
    mutationFn: async (newSettings: SettingsData) => {
      const response = await fetch('http://localhost:8000/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSettings),
      })
      if (!response.ok) {
        throw new Error('Failed to update settings')
      }
      return response.json()
    },
    onSuccess: (data) => {
      toast.success('Settings updated successfully')
      setHasUnsavedChanges(false)
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
    onError: (error) => {
      toast.error('Failed to update settings')
      console.error('Settings update error:', error)
    },
  })

  // Initialize local settings when data is loaded
  useEffect(() => {
    if (settings && !localSettings) {
      setLocalSettings(settings)
    }
  }, [settings, localSettings])

  // Handle settings changes
  const handleSettingChange = (category: keyof SettingsData, key: string, value: any) => {
    if (!localSettings) return

    const newSettings = {
      ...localSettings,
      [category]: {
        ...localSettings[category],
        [key]: value
      }
    }
    
    setLocalSettings(newSettings)
    setHasUnsavedChanges(true)
  }

  // Save settings
  const handleSaveSettings = () => {
    if (localSettings) {
      updateSettingsMutation.mutate(localSettings)
    }
  }

  // Reset settings
  const handleResetSettings = () => {
    if (settings) {
      setLocalSettings(settings)
      setHasUnsavedChanges(false)
      toast.success('Settings reset to saved values')
    }
  }

  const tabs = [
    { id: 'analysis', name: 'Analysis', icon: ChartBarIcon },
    { id: 'data', name: 'Data Sources', icon: CloudIcon },
    { id: 'models', name: 'ML Models', icon: CpuChipIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'performance', name: 'Performance', icon: ServerIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
  ]

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner text="Loading settings..." />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="p-8 text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to Load Settings</h3>
          <p className="text-gray-500 mb-4">Unable to retrieve configuration settings.</p>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['settings'] })}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Retry
          </button>
        </Card>
      </div>
    )
  }

  const renderAnalysisSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Correlation Method
        </label>
        <select
          value={localSettings?.analysis_settings.correlation_method || ''}
          onChange={(e) => handleSettingChange('analysis_settings', 'correlation_method', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="pearson">Pearson</option>
          <option value="spearman">Spearman</option>
          <option value="kendall">Kendall</option>
        </select>
        <p className="text-sm text-gray-500 mt-1">Method for calculating correlation coefficients</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Rolling Window (Days)
        </label>
        <input
          type="number"
          min="1"
          max="365"
          value={localSettings?.analysis_settings.rolling_window || ''}
          onChange={(e) => handleSettingChange('analysis_settings', 'rolling_window', parseInt(e.target.value))}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <p className="text-sm text-gray-500 mt-1">Number of days for rolling window calculations</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Investment Horizon
        </label>
        <select
          value={localSettings?.analysis_settings.investment_horizon || ''}
          onChange={(e) => handleSettingChange('analysis_settings', 'investment_horizon', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="1M">1 Month</option>
          <option value="3M">3 Months</option>
          <option value="6M">6 Months</option>
          <option value="1Y">1 Year</option>
          <option value="2Y">2 Years</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Risk Tolerance
        </label>
        <select
          value={localSettings?.analysis_settings.risk_tolerance || ''}
          onChange={(e) => handleSettingChange('analysis_settings', 'risk_tolerance', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="conservative">Conservative</option>
          <option value="moderate">Moderate</option>
          <option value="aggressive">Aggressive</option>
        </select>
      </div>
    </div>
  )

  const renderDataSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Update Frequency
        </label>
        <select
          value={localSettings?.data_settings.update_frequency || ''}
          onChange={(e) => handleSettingChange('data_settings', 'update_frequency', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="real-time">Real-time</option>
          <option value="hourly">Hourly</option>
          <option value="daily">Daily</option>
        </select>
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={localSettings?.data_settings.auto_etl || false}
            onChange={(e) => handleSettingChange('data_settings', 'auto_etl', e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="ml-2 text-sm text-gray-700">Enable Automatic ETL</span>
        </label>
        <p className="text-sm text-gray-500 mt-1">Automatically run data collection pipelines</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ETL Schedule
        </label>
        <select
          value={localSettings?.data_settings.etl_schedule || ''}
          onChange={(e) => handleSettingChange('data_settings', 'etl_schedule', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="hourly">Every Hour</option>
          <option value="daily_02_00">Daily at 2:00 AM</option>
          <option value="daily_06_00">Daily at 6:00 AM</option>
          <option value="weekly">Weekly</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Data Retention Period
        </label>
        <select
          value={localSettings?.data_settings.data_retention || ''}
          onChange={(e) => handleSettingChange('data_settings', 'data_retention', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="1_year">1 Year</option>
          <option value="2_years">2 Years</option>
          <option value="5_years">5 Years</option>
          <option value="unlimited">Unlimited</option>
        </select>
      </div>
    </div>
  )

  const renderModelSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          GARCH Model Order [p, q]
        </label>
        <div className="grid grid-cols-2 gap-4">
          <input
            type="number"
            min="0"
            max="5"
            value={localSettings?.model_settings.garch_order[0] || 1}
            onChange={(e) => {
              const newOrder = [...(localSettings?.model_settings.garch_order || [1, 1])]
              newOrder[0] = parseInt(e.target.value)
              handleSettingChange('model_settings', 'garch_order', newOrder)
            }}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="p"
          />
          <input
            type="number"
            min="0"
            max="5"
            value={localSettings?.model_settings.garch_order[1] || 1}
            onChange={(e) => {
              const newOrder = [...(localSettings?.model_settings.garch_order || [1, 1])]
              newOrder[1] = parseInt(e.target.value)
              handleSettingChange('model_settings', 'garch_order', newOrder)
            }}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="q"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          VAR Maximum Lags
        </label>
        <input
          type="number"
          min="1"
          max="20"
          value={localSettings?.model_settings.var_max_lags || ''}
          onChange={(e) => handleSettingChange('model_settings', 'var_max_lags', parseInt(e.target.value))}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ML Lookback Period (Days)
        </label>
        <input
          type="number"
          min="30"
          max="365"
          value={localSettings?.model_settings.ml_lookback_period || ''}
          onChange={(e) => handleSettingChange('model_settings', 'ml_lookback_period', parseInt(e.target.value))}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={localSettings?.model_settings.ensemble_models || false}
            onChange={(e) => handleSettingChange('model_settings', 'ensemble_models', e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="ml-2 text-sm text-gray-700">Enable Ensemble Models</span>
        </label>
        <p className="text-sm text-gray-500 mt-1">Use multiple models for better predictions</p>
      </div>
    </div>
  )

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={localSettings?.notification_settings.email_alerts || false}
            onChange={(e) => handleSettingChange('notification_settings', 'email_alerts', e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="ml-2 text-sm text-gray-700">Email Alerts</span>
        </label>
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={localSettings?.notification_settings.slack_alerts || false}
            onChange={(e) => handleSettingChange('notification_settings', 'slack_alerts', e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="ml-2 text-sm text-gray-700">Slack Alerts</span>
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Alert Threshold
        </label>
        <input
          type="number"
          min="0"
          max="1"
          step="0.1"
          value={localSettings?.notification_settings.alert_threshold || ''}
          onChange={(e) => handleSettingChange('notification_settings', 'alert_threshold', parseFloat(e.target.value))}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <p className="text-sm text-gray-500 mt-1">Threshold for triggering alerts (0.0 - 1.0)</p>
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={localSettings?.notification_settings.daily_reports || false}
            onChange={(e) => handleSettingChange('notification_settings', 'daily_reports', e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="ml-2 text-sm text-gray-700">Daily Reports</span>
        </label>
      </div>
    </div>
  )

  const renderPerformanceSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={localSettings?.performance_settings.cache_enabled || false}
            onChange={(e) => handleSettingChange('performance_settings', 'cache_enabled', e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="ml-2 text-sm text-gray-700">Enable Caching</span>
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Batch Size
        </label>
        <input
          type="number"
          min="10"
          max="1000"
          value={localSettings?.performance_settings.batch_size || ''}
          onChange={(e) => handleSettingChange('performance_settings', 'batch_size', parseInt(e.target.value))}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Concurrent Requests
        </label>
        <input
          type="number"
          min="1"
          max="50"
          value={localSettings?.performance_settings.concurrent_requests || ''}
          onChange={(e) => handleSettingChange('performance_settings', 'concurrent_requests', parseInt(e.target.value))}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timeout (Seconds)
        </label>
        <input
          type="number"
          min="5"
          max="300"
          value={localSettings?.performance_settings.timeout_seconds || ''}
          onChange={(e) => handleSettingChange('performance_settings', 'timeout_seconds', parseInt(e.target.value))}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
    </div>
  )

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <ExclamationTriangleIcon className="w-5 h-5 text-yellow-400 mr-2 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-yellow-800">Security Configuration</h4>
            <p className="text-sm text-yellow-700 mt-1">
              Security settings are managed through environment variables and configuration files for enhanced security.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-gray-700">API Security</h4>
          <p className="text-sm text-gray-500">Configure API authentication and rate limiting</p>
        </div>
        
        <div>
          <h4 className="text-sm font-medium text-gray-700">Data Encryption</h4>
          <p className="text-sm text-gray-500">Enable encryption for sensitive data storage</p>
        </div>
        
        <div>
          <h4 className="text-sm font-medium text-gray-700">Access Control</h4>
          <p className="text-sm text-gray-500">Manage user permissions and access levels</p>
        </div>
      </div>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'analysis':
        return renderAnalysisSettings()
      case 'data':
        return renderDataSettings()
      case 'models':
        return renderModelSettings()
      case 'notifications':
        return renderNotificationSettings()
      case 'performance':
        return renderPerformanceSettings()
      case 'security':
        return renderSecuritySettings()
      default:
        return renderAnalysisSettings()
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Configure system parameters and preferences</p>
        </div>
        <div className="flex items-center space-x-4">
          {hasUnsavedChanges && (
            <span className="text-sm text-yellow-600 bg-yellow-100 px-3 py-1 rounded-full">
              Unsaved changes
            </span>
          )}
          <button
            onClick={handleResetSettings}
            disabled={!hasUnsavedChanges}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Reset
          </button>
          <button
            onClick={handleSaveSettings}
            disabled={!hasUnsavedChanges || updateSettingsMutation.isPending}
            className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updateSettingsMutation.isPending ? (
              <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <CheckIcon className="w-4 h-4 mr-2" />
            )}
            Save Changes
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <Card>
            <nav className="p-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {tab.name}
                  </button>
                )
              })}
            </nav>
          </Card>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          <Card>
            <div className="p-6">
              <div className="flex items-center mb-6">
                {(() => {
                  const activeTabData = tabs.find(tab => tab.id === activeTab)
                  const Icon = activeTabData?.icon || Cog6ToothIcon
                  return (
                    <>
                      <Icon className="w-6 h-6 text-primary-600 mr-3" />
                      <h2 className="text-xl font-bold text-gray-900">
                        {activeTabData?.name || 'Settings'}
                      </h2>
                    </>
                  )
                })()}
              </div>
              
              <div className="max-w-2xl">
                {renderTabContent()}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Settings 