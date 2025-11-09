import React from 'react'
import { X, CheckCircle, AlertTriangle, Info, AlertCircle } from 'lucide-react'

function QAValidationModal({ validation, onClose }) {
  if (!validation) return null

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      default:
        return <Info className="h-5 w-5 text-blue-600" />
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800'
    }
  }

  const getQualityColor = (score) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Quality Assurance Report</h2>
              <p className="text-blue-100 text-sm">
                Automated validation • {validation.file_type?.toUpperCase()} Analysis
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          {/* Quality Score */}
          <div className="mt-6 flex items-center space-x-6">
            <div className="bg-white bg-opacity-20 rounded-lg px-6 py-3">
              <div className="text-sm text-blue-100 mb-1">Quality Score</div>
              <div className={`text-4xl font-bold ${validation.quality_score >= 90 ? 'text-green-300' : validation.quality_score >= 70 ? 'text-yellow-300' : 'text-red-300'}`}>
                {validation.quality_score}/100
              </div>
            </div>
            <div className="flex-1 grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-red-300">{validation.critical_issues}</div>
                <div className="text-xs text-blue-100">Critical</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-300">{validation.warnings}</div>
                <div className="text-xs text-blue-100">Warnings</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-300">{validation.info_messages}</div>
                <div className="text-xs text-blue-100">Info</div>
              </div>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        {validation.summary && (
          <div className="bg-gray-50 p-4 border-b border-gray-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              {Object.entries(validation.summary).map(([key, value]) => (
                <div key={key} className="text-center">
                  <div className="font-semibold text-gray-900">{value}</div>
                  <div className="text-xs text-gray-600 capitalize">
                    {key.replace(/_/g, ' ')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Issues List */}
        <div className="flex-1 overflow-y-auto p-6">
          {validation.issues && validation.issues.length > 0 ? (
            <div className="space-y-3">
              {['critical', 'warning', 'info'].map(severity => {
                const severityIssues = validation.issues.filter(i => i.severity === severity)
                if (severityIssues.length === 0) return null

                return (
                  <div key={severity}>
                    <h3 className="font-semibold text-gray-900 mb-3 capitalize flex items-center space-x-2">
                      {getSeverityIcon(severity)}
                      <span>{severity} ({severityIssues.length})</span>
                    </h3>
                    <div className="space-y-2">
                      {severityIssues.map((issue, idx) => (
                        <div
                          key={idx}
                          className={`border rounded-lg p-4 ${getSeverityColor(issue.severity)}`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="font-mono text-xs bg-white bg-opacity-50 px-2 py-1 rounded">
                                  {issue.location}
                                </span>
                                <span className="text-xs font-semibold uppercase">
                                  {issue.category.replace(/_/g, ' ')}
                                </span>
                              </div>
                              <p className="text-sm font-medium mb-2">{issue.message}</p>
                              
                              {issue.formula && (
                                <div className="bg-white bg-opacity-50 rounded p-2 mb-2">
                                  <div className="text-xs text-gray-600 mb-1">Formula:</div>
                                  <code className="text-xs font-mono">{issue.formula}</code>
                                </div>
                              )}
                              
                              {issue.value && (
                                <div className="text-xs mb-2">
                                  <span className="text-gray-600">Value: </span>
                                  <span className="font-mono">{issue.value}</span>
                                </div>
                              )}
                              
                              {issue.suggestion && (
                                <div className="bg-white bg-opacity-70 rounded p-2 mt-2">
                                  <div className="text-xs font-semibold text-gray-700 mb-1">💡 Suggestion:</div>
                                  <div className="text-xs text-gray-700">{issue.suggestion}</div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Perfect Quality!</h3>
              <p className="text-gray-600">No issues detected in this file.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="btn btn-primary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default QAValidationModal
