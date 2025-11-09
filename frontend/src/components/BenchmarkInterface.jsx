import React, { useState, useEffect } from 'react'
import { FileSpreadsheet, Play, CheckCircle, AlertCircle, Loader, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import { executeBenchmarkTask } from '../services/benchmark'
import ReferenceFilePreview from './ReferenceFilePreview'

function BenchmarkInterface({ onResultReady }) {
  const [executing, setExecuting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('')
  const [tasks, setTasks] = useState([])
  const [selectedTask, setSelectedTask] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedTask, setExpandedTask] = useState(null)

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/v1/benchmark/tasks')
      const data = await response.json()
      setTasks(data.tasks || [])
      if (data.tasks && data.tasks.length > 0) {
        setSelectedTask(data.tasks[0])
      }
      setLoading(false)
    } catch (error) {
      console.error('Failed to load tasks:', error)
      setLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!selectedTask) {
      toast.error('Please select a task')
      return
    }

    setExecuting(true)
    setProgress(0)
    setStatus('Initializing task execution...')

    try {
      await executeBenchmarkTask(selectedTask.task_id, {
        onProgress: (message, progressValue) => {
          setStatus(message)
          setProgress(progressValue)
        },
        onComplete: (result) => {
          setProgress(100)
          setStatus('Complete!')
          toast.success('Excel report generated successfully!')

          if (onResultReady) {
            onResultReady(result)
          }

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

  if (loading) {
    return (
      <div className="card text-center py-12">
        <Loader className="h-8 w-8 text-blue-600 animate-spin mx-auto mb-3" />
        <p className="text-gray-600">Loading tasks...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Task Selector */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3">Select Task</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {tasks.map((task) => (
            <div key={task.task_id} className="border-2 rounded-lg overflow-hidden">
              <button
                onClick={() => {
                  setSelectedTask(task)
                  setExpandedTask(expandedTask === task.task_id ? null : task.task_id)
                }}
                className={`w-full p-3 text-left transition-colors ${
                  selectedTask?.task_id === task.task_id
                    ? 'bg-blue-50 border-blue-500'
                    : 'bg-white hover:bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <div className={`h-4 w-4 rounded-full border-2 flex items-center justify-center ${
                        selectedTask?.task_id === task.task_id
                          ? 'border-blue-600 bg-blue-600'
                          : 'border-gray-300'
                      }`}>
                        {selectedTask?.task_id === task.task_id && (
                          <CheckCircle className="h-3 w-3 text-white" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {task.sector || 'Sales Task'}
                        </p>
                        {task.has_reference_files && (
                          <span className="text-xs text-blue-600">Has reference files</span>
                        )}
                      </div>
                    </div>
                  </div>
                  {expandedTask === task.task_id ? (
                    <ChevronUp className="h-5 w-5 text-gray-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0" />
                  )}
                </div>
              </button>
              
              {expandedTask === task.task_id && (
                <div className="p-4 bg-gray-50 border-t border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Task Description:</h4>
                  <div className="bg-white border border-gray-200 rounded p-3 mb-4">
                    <p className="text-sm text-gray-700 whitespace-pre-line">
                      {task.full_prompt}
                    </p>
                  </div>
                  
                  {task.reference_file_urls && task.reference_file_urls.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">Reference Files:</h4>
                      <div className="space-y-4">
                        {task.reference_file_urls.map((url, idx) => {
                          const fileName = url.split('/').pop()
                          return (
                            <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4">
                              <ReferenceFilePreview 
                                fileUrl={url}
                                fileName={fileName}
                              />
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Execute Button */}
      <div className="card">
        {!executing ? (
          <button
            onClick={handleExecute}
            disabled={!selectedTask}
            className="btn btn-primary w-full flex items-center justify-center space-x-2 text-lg py-4"
          >
            <Play className="h-5 w-5" />
            <span>Execute Selected Task</span>
          </button>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <Loader className="h-5 w-5 text-blue-600 animate-spin flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{status}</p>
                <div className="mt-2 bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-blue-600 h-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{progress}% complete</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BenchmarkInterface
