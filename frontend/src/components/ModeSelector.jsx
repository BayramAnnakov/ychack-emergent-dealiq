import React from 'react'
import { Zap, Award } from 'lucide-react'

function ModeSelector({ mode, onModeChange }) {
  return (
    <div className="inline-flex items-center bg-gray-100 rounded-lg p-1">
      <button
        onClick={() => onModeChange('crm')}
        className={`
          flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all
          ${mode === 'crm'
            ? 'bg-white text-primary-700 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
          }
        `}
      >
        <Zap className="h-4 w-4" />
        <span>Quick Analysis</span>
      </button>
      <button
        onClick={() => onModeChange('benchmark')}
        className={`
          flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all
          ${mode === 'benchmark'
            ? 'bg-white text-green-700 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
          }
        `}
      >
        <Award className="h-4 w-4" />
        <span>Professional Reports</span>
        <span className="ml-1 px-2 py-0.5 text-xs font-semibold bg-green-100 text-green-700 rounded-full">
          GDPval
        </span>
      </button>
    </div>
  )
}

export default ModeSelector
