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
  const [progressLog, setProgressLog] = useState([])
  const [costUsd, setCostUsd] = useState(0)
  const [tokensUsed, setTokensUsed] = useState(0)
  const [activeSkills, setActiveSkills] = useState([])
  const [showConfetti, setShowConfetti] = useState(false)
  const [executionPhases, setExecutionPhases] = useState([
    { name: 'Initialize', status: 'pending', icon: '🚀' },
    { name: 'Analyze', status: 'pending', icon: '🔍' },
    { name: 'Generate', status: 'pending', icon: '✍️' },
    { name: 'Validate', status: 'pending', icon: '✅' }
  ]) // Track all progress messages

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/v1/benchmark/tasks')
      const data = await response.json()
      console.log('Loaded tasks:', data.tasks)
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
    setProgressLog([])
    setCostUsd(0)
    setTokensUsed(0)
    setActiveSkills([])
    setShowConfetti(false)
    setExecutionPhases([
      { name: 'Initialize', status: 'active', icon: '🚀' },
      { name: 'Analyze', status: 'pending', icon: '🔍' },
      { name: 'Generate', status: 'pending', icon: '✍️' },
      { name: 'Validate', status: 'pending', icon: '✅' }
    ])

    try {
      await executeBenchmarkTask(selectedTask.task_id, {
        onProgress: (message, progressValue, extras = {}) => {
          setStatus(message)
          setProgress(progressValue)
          
          // Update cost and tokens
          if (extras.costUsd !== undefined) setCostUsd(extras.costUsd)
          if (extras.tokens !== undefined) setTokensUsed(extras.tokens)
          if (extras.activeSkills) setActiveSkills(extras.activeSkills)
          
          // Update execution phases based on progress
          setExecutionPhases(phases => {
            const newPhases = [...phases]
            if (progressValue >= 20 && progressValue < 50) {
              newPhases[0].status = 'complete'
              newPhases[1].status = 'active'
            } else if (progressValue >= 50 && progressValue < 80) {
              newPhases[1].status = 'complete'
              newPhases[2].status = 'active'
            } else if (progressValue >= 80) {
              newPhases[2].status = 'complete'
              newPhases[3].status = 'active'
            }
            return newPhases
          })
          
          // Add to progress log
          setProgressLog(prev => [...prev, { 
            message, 
            time: new Date().toLocaleTimeString(), 
            progress: progressValue,
            skills: extras.activeSkills
          }])
        },
        onComplete: (result) => {
          setProgress(100)
          setStatus('Complete!')
          
          // Dynamic success message based on file type
          const isPdf = result.file_name?.endsWith('.pdf')
          toast.success(isPdf ? 'PDF report generated successfully!' : 'Excel report generated successfully!')

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
      {!executing ? (
        <>
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
                              {task.title || task.sector || 'Sales Task'}
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
            <button
              onClick={handleExecute}
              disabled={!selectedTask}
              className="btn btn-primary w-full flex items-center justify-center space-x-2 text-lg py-4"
            >
              <Play className="h-5 w-5" />
              <span>Execute Selected Task</span>
            </button>
          </div>
        </>
      ) : (
        /* Centered Progress Display */
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl p-8 max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <Loader className="h-8 w-8 text-blue-600 animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {selectedTask?.title || 'Executing Task'}
              </h2>
              <p className="text-gray-600">
                Claude Agent SDK is working on your professional report...
              </p>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-full transition-all duration-300 flex items-center justify-end"
                  style={{ width: `${progress}%` }}
                >
                  <span className="text-white text-xs font-bold pr-2">
                    {progress}%
                  </span>
                </div>
              </div>
            </div>

            {/* Current Status */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <p className="text-sm font-medium text-gray-900">{status}</p>
            </div>

            {/* Activity Log */}
            <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-y-auto min-h-[200px] max-h-[350px] border border-gray-200">
              <h3 className="text-xs font-semibold text-gray-700 mb-3 sticky top-0 bg-gray-50">Activity Log:</h3>
              <div className="space-y-2">
                {progressLog.slice(-15).map((entry, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-xs">
                    <span className="text-gray-400 flex-shrink-0 font-mono">{entry.time}</span>
                    <span className="text-gray-700 flex-1">{entry.message}</span>
                    <span className="text-gray-400 flex-shrink-0">{entry.progress}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Additional Info */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center text-xs">
                <div>
                  <p className="text-gray-500">Skills Active</p>
                  <p className="font-semibold text-blue-600">xlsx, pdf</p>
                </div>
                <div>
                  <p className="text-gray-500">AI Model</p>
                  <p className="font-semibold text-purple-600">Claude Sonnet</p>
                </div>
                <div>
                  <p className="text-gray-500">Est. Time</p>
                  <p className="font-semibold text-gray-700">1-3 min</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BenchmarkInterface
