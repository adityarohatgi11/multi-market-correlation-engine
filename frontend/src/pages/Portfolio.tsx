import React from 'react';
import { motion } from 'framer-motion';
import Card from '@/components/ui/Card';

const Portfolio: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
        <p className="text-gray-600 mt-2">
          Portfolio optimization and recommendations
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <Card>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Portfolio Management</h2>
          <p className="text-gray-600">
            Advanced portfolio optimization and recommendation features coming soon...
          </p>
        </Card>
      </motion.div>
    </div>
  );
};

export default Portfolio;
