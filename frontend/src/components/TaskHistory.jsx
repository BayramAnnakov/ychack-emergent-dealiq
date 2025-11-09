import React, { useState, useEffect } from 'react'
import { Clock, FileSpreadsheet, Download, Eye, Table } from 'lucide-react'
import { getTaskHistory, downloadExcelResult } from '../services/benchmark'
import ExcelPreview from './ExcelPreview'

function TaskHistory() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState(null)
  const [showPreview, setShowPreview] = useState(false)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      setLoading(true)
      const data = await getTaskHistory()
      setHistory(data.tasks || [])
      setLoading(false)
    } catch (error) {
      console.error('Failed to load history:', error)
      setLoading(false)
    }
  }

  const formatDate = (isoDate) => {
    const date = new Date(isoDate)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    
    return date.toLocaleDateString()
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const handleViewTask = (task) => {
    setSelectedTask(task)
    setShowPreview(true)
  }

  const handleClosePreview = () => {
    setShowPreview(false)
    setSelectedTask(null)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Clock className="h-12 w-12 text-gray-400 mx-auto mb-3 animate-spin" />
          <p className="text-gray-600">Loading task history...</p>
        </div>
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div className="text-center py-12">
        <FileSpreadsheet className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No completed tasks yet</h3>
        <p className="text-gray-600">
          Execute a benchmark task to see it appear here
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Task History</h2>
          <p className="text-gray-600 mt-1">
            {history.length} completed task{history.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button
          onClick={loadHistory}
          className="btn btn-sm btn-secondary"
        >
          Refresh
        </button>
      </div>

      {/* Preview Modal */}
      {showPreview && selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {selectedTask.file_name}
                </h3>
                <p className="text-sm text-gray-600">
                  Created {formatDate(selectedTask.created_at)}
                </p>
              </div>
              <button
                onClick={handleClosePreview}
                className="btn btn-sm btn-secondary"
              >
                Close
              </button>
            </div>
            <div className="p-6">
              <ExcelPreview 
                taskId={selectedTask.task_id}
                fileName={selectedTask.file_name}
              />
            </div>
          </div>
        </div>
      )}

      {/* Task List */}
      <div className="grid grid-cols-1 gap-4">
        {history.map((task) => (
          <div
            key={task.task_id}
            className="card hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                <div className="bg-green-100 rounded-lg p-3">
                  <FileSpreadsheet className="h-6 w-6 text-green-600" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {task.file_name}
                  </h3>
                  
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <Clock className="h-4 w-4" />
                      <span>{formatDate(task.modified_at)}</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Table className="h-4 w-4" />
                      <span>{task.sheet_count} sheets</span>
                    </div>
                    
                    <div className="text-gray-500">
                      {formatFileSize(task.file_size)}
                    </div>
                  </div>

                  {task.sheet_names && task.sheet_names.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {task.sheet_names.map((sheet, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
                        >
                          {sheet}
                        </span>
                      ))}
                      {task.sheet_count > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          +{task.sheet_count - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-2 ml-4 flex-shrink-0">
                <button
                  onClick={() => handleViewTask(task)}
                  className="btn btn-sm btn-secondary flex items-center space-x-1 w-full sm:w-auto"
                >
                  <Eye className="h-4 w-4" />
                  <span>Preview</span>
                </button>
                
                <button
                  onClick={() => downloadExcelResult(task.task_id)}
                  className="btn btn-sm btn-primary flex items-center space-x-1 w-full sm:w-auto"
                >
                  <Download className="h-4 w-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TaskHistory
