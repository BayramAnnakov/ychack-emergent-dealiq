import React, { useState } from 'react'
import { FileSpreadsheet, Play, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import toast from 'react-hot-toast'
import { executeBenchmarkTask } from '../services/benchmark'

function BenchmarkInterface({ onResultReady }) {
  const [executing, setExecuting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('')

  // Sample GDPval task (you can load this from API later)
  const task = {
    id: '19403010-3e5c-494e-a6d3-13594e99f6af',
    title: 'XR Retailer 2023 Makeup Sales Analysis',
    description: 'Comprehensive sales performance analysis including YoY comparison, discontinued SKU risk assessment, volume drivers analysis, and strategic recommendations.',
    category: 'Sales Analytics',
    difficulty: 3,
    estimatedTime: '45-60 seconds',
    sections: [
      'Overall Business Performance',
      'Discontinued SKUs Risk Analysis',
      'Top Volume Drivers',
      'Volume Increases & Decreases',
      'Strategic Recommendations'
    ]
  }

  const handleExecute = async () => {
    setExecuting(true)
    setProgress(0)
    setStatus('Initializing task execution...')

    try {
      // Execute task with real API
      await executeBenchmarkTask(task.id, {
        onProgress: (message, progressValue) => {
          setStatus(message)
          setProgress(progressValue)
        },
        onComplete: (result) => {
          setProgress(100)
          setStatus('Complete!')
          toast.success('Excel report generated successfully!')

          // Notify parent with result
          if (onResultReady) {
            onResultReady(result)
          }

          // Reset after a delay
          setTimeout(() => {
            setExecuting(false)
            setProgress(0)
            setStatus('')
          }, 2000)
        },
        onError: (error) => {
          toast.error(error.message || 'Failed to execute task')
          setStatus('Failed')
          setExecuting(false)
        }
      })
    } catch (error) {
      toast.error(error.message || 'Failed to execute task')
      setStatus('Failed')
      setExecuting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Task Card */}
      <div className="card">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <FileSpreadsheet className="h-5 w-5 text-green-600" />
              <span className="text-xs font-semibold text-green-700 bg-green-100 px-2 py-0.5 rounded-full">
                {task.category}
              </span>
              <span className="text-xs text-gray-500">
                {'⭐'.repeat(task.difficulty)}
              </span>
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">{task.title}</h2>
            <p className="text-sm text-gray-600 mb-4">{task.description}</p>
          </div>
        </div>

        <div className="border-t pt-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Report Sections:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
            {task.sections.map((section, idx) => (
              <div key={idx} className="flex items-center space-x-2 text-sm text-gray-600">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>{section}</span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-gray-500">
              <span className="font-medium">Estimated time:</span> {task.estimatedTime}
            </div>
            <button
              onClick={handleExecute}
              disabled={executing}
              className="btn btn-primary flex items-center space-x-2"
            >
              {executing ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Executing...</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  <span>Execute Task</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Execution Progress */}
      {executing && (
        <div className="card bg-blue-50 border-blue-200">
          <div className="flex items-start space-x-3">
            <Loader className="h-5 w-5 text-blue-600 animate-spin mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-blue-900 mb-1">Task Executing</h3>
              <p className="text-sm text-blue-700 mb-3">{status}</p>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-blue-600">Progress</span>
                <span className="text-xs font-semibold text-blue-700">{Math.round(progress)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info Panel */}
      <div className="card bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
        <div className="flex items-start space-x-3">
          <div className="bg-green-100 p-2 rounded-lg">
            <AlertCircle className="h-5 w-5 text-green-700" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-1">GDPval Benchmark Integration</h3>
            <p className="text-sm text-gray-600 mb-2">
              This task is from OpenAI's GDPval benchmark - the gold standard for evaluating AI performance on real-world sales analytics.
            </p>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-2 py-1 bg-white rounded-md text-gray-700 border border-gray-200">
                ✓ 100% Formula-based
              </span>
              <span className="px-2 py-1 bg-white rounded-md text-gray-700 border border-gray-200">
                ✓ Validated Output
              </span>
              <span className="px-2 py-1 bg-white rounded-md text-gray-700 border border-gray-200">
                ✓ Executive-Ready
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BenchmarkInterface
