import React from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import type { CardProps } from '@/types'

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  action,
  loading = false,
  className = '',
  children,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        'bg-white rounded-xl shadow-card border border-gray-200 overflow-hidden',
        className
      )}
    >
      {(title || subtitle || action) && (
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              {title && (
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              )}
              {subtitle && (
                <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
              )}
            </div>
            {action && <div>{action}</div>}
          </div>
        </div>
      )}
      
      <div className={clsx('p-6', { 'animate-pulse': loading })}>
        {loading ? (
          <div className="space-y-3">
            <div className="h-4 bg-gray-300 rounded w-3/4"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2"></div>
            <div className="h-32 bg-gray-300 rounded"></div>
          </div>
        ) : (
          children
        )}
      </div>
    </motion.div>
  )
}

export default Card 