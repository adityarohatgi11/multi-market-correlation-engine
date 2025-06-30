import React from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import type { LoadingProps } from '@/types'

const LoadingSpinner: React.FC<LoadingProps> = ({
  size = 'md',
  text,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <div className={clsx('flex flex-col items-center justify-center', className)}>
      <motion.div
        className={clsx(
          'border-2 border-gray-300 border-t-primary-600 rounded-full',
          sizeClasses[size]
        )}
        animate={{ rotate: 360 }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      {text && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-sm text-gray-500 mt-2"
        >
          {text}
        </motion.p>
      )}
    </div>
  )
}

export default LoadingSpinner 