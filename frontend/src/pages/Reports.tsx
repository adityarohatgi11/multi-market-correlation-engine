import React from 'react'
import { motion } from 'framer-motion'
import Card from '@/components/ui/Card'

const Reports: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600 mt-2">
          Analytics and performance reports
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <Card>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Analytics Reports</h2>
          <p className="text-gray-600">
            Comprehensive reporting and analytics dashboard coming soon...
          </p>
        </Card>
      </motion.div>
    </div>
  )
}

export default Reports 