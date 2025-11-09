import React, { useState, useEffect } from 'react'
import { Clock, Brain, Eye, TrendingUp } from 'lucide-react'

function AnalysisHistory({ onSelectAnalysis }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/v1/insights/history')
      const data = await response.json()
      setHistory(data.analyses || [])
      setLoading(false)
    } catch (error) {
      console.error('Failed to load history:', error)
      setLoading(false)
    }
  }

  const handleViewAnalysis = async (analysisId) => {
    try {
      const response = await fetch(`/api/v1/insights/history/${analysisId}`)
      const data = await response.json()
      
      // Pass to parent to display
      if (onSelectAnalysis) {
        onSelectAnalysis(data)
      }
    } catch (error) {
      console.error('Failed to load analysis:', error)
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Clock className="h-12 w-12 text-gray-400 mx-auto mb-3 animate-spin" />
          <p className="text-gray-600">Loading analysis history...</p>
        </div>
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div className="text-center py-12">
        <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No analyses yet</h3>
        <p className="text-gray-600">
          Run a CRM analysis to see it appear here
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analysis History</h2>
          <p className="text-gray-600 mt-1">
            {history.length} saved analysis{history.length !== 1 ? 'es' : ''}
          </p>
        </div>
        <button
          onClick={loadHistory}
          className="btn btn-sm btn-secondary"
        >
          Refresh
        </button>
      </div>

      {/* Analysis List */}
      <div className="grid grid-cols-1 gap-4">
        {history.map((analysis) => (
          <div
            key={analysis.analysis_id}
            className="card hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                <div className="bg-blue-100 rounded-lg p-3">
                  <Brain className="h-6 w-6 text-blue-600" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {analysis.query}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                    {analysis.preview}
                  </p>
                  
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <Clock className="h-4 w-4" />
                      <span>{formatDate(analysis.created_at)}</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <TrendingUp className="h-4 w-4" />
                      <span>{analysis.insight_count} insights</span>
                    </div>
                    
                    <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded capitalize">
                      {analysis.query_type}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleViewAnalysis(analysis.analysis_id)}
                className="btn btn-sm btn-primary flex items-center space-x-1 ml-4 flex-shrink-0"
              >
                <Eye className="h-4 w-4" />
                <span>View</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AnalysisHistory
