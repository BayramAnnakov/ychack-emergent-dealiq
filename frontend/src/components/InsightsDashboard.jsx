import React from 'react'
import { Lightbulb, TrendingUp, AlertTriangle, CheckCircle, Target, Activity } from 'lucide-react'

function InsightsDashboard({ insights, isLoading }) {
  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <div>
            <h3 className="text-lg font-semibold">Analyzing your data...</h3>
            <p className="text-sm text-gray-600">Our AI agents are working on your request</p>
          </div>
        </div>
      </div>
    )
  }

  if (!insights || insights.length === 0) {
    return null
  }

  const getInsightIcon = (type) => {
    const iconMap = {
      'pipeline_health': Activity,
      'win_rate': Target,
      'sales_cycle': TrendingUp,
      'growth_trend': TrendingUp,
      'top_performers': CheckCircle,
      'closure_prediction': Target,
      'churn_risk': AlertTriangle,
      'hypothesis_test': Lightbulb
    }
    return iconMap[type] || Lightbulb
  }

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.8) return 'text-success-600 bg-success-50'
    if (confidence > 0.6) return 'text-warning-600 bg-warning-50'
    return 'text-gray-600 bg-gray-50'
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 flex items-center">
          <Lightbulb className="h-5 w-5 mr-2 text-primary-600" />
          AI-Generated Insights
        </h2>

        <div className="space-y-3">
          {insights.slice(0, 10).map((insight, index) => {
            const Icon = getInsightIcon(insight.type)

            return (
              <div
                key={index}
                className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-start space-x-3">
                  <div className="bg-white p-2 rounded-lg">
                    <Icon className="h-5 w-5 text-primary-600" />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-medium text-gray-900">
                        {insight.title || 'Insight'}
                      </h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${getConfidenceColor(insight.confidence || 0.5)}`}>
                        {((insight.confidence || 0.5) * 100).toFixed(0)}% confidence
                      </span>
                    </div>

                    <p className="text-sm text-gray-700 mb-2">
                      {insight.description}
                    </p>

                    {insight.data && Object.keys(insight.data).length > 0 && (
                      <div className="bg-white rounded p-2 mt-2">
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {Object.entries(insight.data).slice(0, 4).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-gray-500">
                                {key.replace(/_/g, ' ').charAt(0).toUpperCase() + key.replace(/_/g, ' ').slice(1)}:
                              </span>
                              <span className="ml-1 font-medium text-gray-900">
                                {typeof value === 'number'
                                  ? value.toLocaleString()
                                  : Array.isArray(value)
                                  ? value.length + ' items'
                                  : String(value).substring(0, 50)
                                }
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {insight.source && (
                      <div className="mt-2 text-xs text-gray-500">
                        Source: {insight.source}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default InsightsDashboard