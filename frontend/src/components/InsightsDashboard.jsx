import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Lightbulb, TrendingUp, AlertTriangle, CheckCircle, Target, Activity, ChevronDown, ChevronUp, BarChart3, Sparkles, Zap, FileDown } from 'lucide-react'
import toast from 'react-hot-toast'
import ActionableInsights from './ActionableInsights'
import ExecutiveSummary from './ExecutiveSummary'
import InsightsCharts from './InsightsCharts'
import LoadingSkeleton from './LoadingSkeleton'

function InsightsDashboard({ insights, isLoading }) {
  const [expandedInsights, setExpandedInsights] = useState({})
  const [activeTab, setActiveTab] = useState('insights') // Default to insights-first

  if (isLoading) {
    return <LoadingSkeleton />
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
      'hypothesis_test': Lightbulb,
      'metrics': Activity,
      'analysis': Lightbulb,
      'recommendations': Target
    }
    return iconMap[type] || Lightbulb
  }

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.8) return 'text-success-600 bg-success-50'
    if (confidence > 0.6) return 'text-warning-600 bg-warning-50'
    return 'text-gray-600 bg-gray-50'
  }

  const getConfidenceLabel = (confidence) => {
    if (confidence > 0.8) return 'High'
    if (confidence > 0.6) return 'Medium'
    return 'Low'
  }

  // Extract key metrics from insight data
  const extractKeyMetrics = (data) => {
    if (!data || typeof data !== 'object') return []

    const metrics = []
    const numericKeys = Object.keys(data).filter(key =>
      typeof data[key] === 'number' && !key.toLowerCase().includes('id')
    )

    return numericKeys.slice(0, 3).map(key => ({
      label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: typeof data[key] === 'number' && data[key] % 1 !== 0
        ? data[key].toFixed(2)
        : data[key].toLocaleString()
    }))
  }

  // Helper function to strip markdown and clean text for previews
  const stripMarkdown = (text) => {
    if (!text) return ''
    return text
      .replace(/#{1,6}\s+/g, '') // Remove headers
      .replace(/\*\*(.+?)\*\*/g, '$1') // Remove bold
      .replace(/\*(.+?)\*/g, '$1') // Remove italic
      .replace(/`(.+?)`/g, '$1') // Remove code
      .replace(/\[(.+?)\]\(.+?\)/g, '$1') // Remove links
      .replace(/^\s*[-*+]\s+/gm, '') // Remove list markers
      .replace(/^\s*\d+\.\s+/gm, '') // Remove numbered list markers
      .replace(/\|/g, ' ') // Remove table pipes
      .replace(/\n+/g, ' ') // Replace newlines with spaces
      .replace(/\s+/g, ' ') // Normalize spaces
      .trim()
  }

  const tabs = [
    { id: 'insights', label: 'AI Insights', icon: Zap },
    { id: 'metrics', label: 'Metrics & Charts', icon: BarChart3 },
    { id: 'all', label: 'Full Analysis', icon: Lightbulb }
  ]

  return (
    <div className="space-y-6">
      {/* Tabbed Navigation */}
      <div className="card">
        <div className="border-b border-gray-200 mb-6">
          <nav className="flex space-x-4" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors
                    ${isActive
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'insights' && (
          <ActionableInsights insights={insights} />
        )}

        {activeTab === 'metrics' && (
          <div className="space-y-6">
            <ExecutiveSummary insights={insights} />
            <InsightsCharts insights={insights} />
          </div>
        )}

        {activeTab === 'all' && (
          <div className="space-y-4">
          {insights.slice(0, 10).map((insight, index) => {
            const Icon = getInsightIcon(insight.type)
            const isExpanded = expandedInsights[index]
            const keyMetrics = extractKeyMetrics(insight.data)

            return (
              <div
                key={index}
                className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-5 border border-gray-200 hover:border-primary-200 hover:shadow-md transition-all duration-200 animate-fade-in"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex items-start space-x-4">
                  {/* Icon */}
                  <div className="bg-primary-50 p-3 rounded-xl flex-shrink-0">
                    <Icon className="h-6 w-6 text-primary-600" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    {/* Header */}
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h3 className="font-bold text-gray-900 text-lg leading-tight">
                        {insight.title || 'Insight'}
                      </h3>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        {/* Confidence Badge */}
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-medium px-3 py-1.5 rounded-full ${getConfidenceColor(insight.confidence || 0.5)}`}>
                            {getConfidenceLabel(insight.confidence || 0.5)} Confidence
                          </span>

                          {/* Confidence Meter */}
                          <div className="hidden md:flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map((level) => (
                              <div
                                key={level}
                                className={`h-5 w-1 rounded-full transition-all ${
                                  level <= (insight.confidence || 0.5) * 5
                                    ? 'bg-primary-600'
                                    : 'bg-gray-200'
                                }`}
                              />
                            ))}
                          </div>
                        </div>

                        {/* Expand/Collapse Button */}
                        <button
                          onClick={() => setExpandedInsights(prev => ({
                            ...prev,
                            [index]: !prev[index]
                          }))}
                          className="text-gray-400 hover:text-primary-600 transition-colors p-1 rounded-lg hover:bg-primary-50"
                          aria-label={isExpanded ? "Collapse" : "Expand"}
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-5 w-5" />
                          ) : (
                            <ChevronDown className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Preview or Full Content */}
                    <div className={`transition-all duration-300 ${isExpanded ? 'mb-4' : ''}`}>
                      {isExpanded ? (
                        <div className="prose prose-sm max-w-none">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              // Customize heading styles
                              h1: ({node, ...props}) => <h1 className="text-2xl font-bold mt-6 mb-3 text-gray-900" {...props} />,
                              h2: ({node, ...props}) => <h2 className="text-xl font-bold mt-5 mb-2 text-gray-900" {...props} />,
                              h3: ({node, ...props}) => <h3 className="text-lg font-semibold mt-4 mb-2 text-gray-800" {...props} />,
                              h4: ({node, ...props}) => <h4 className="text-base font-semibold mt-3 mb-1 text-gray-800" {...props} />,

                              // Customize paragraph
                              p: ({node, ...props}) => <p className="text-sm text-gray-700 mb-2 leading-relaxed" {...props} />,

                              // Customize lists
                              ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-1 mb-3 text-sm text-gray-700" {...props} />,
                              ol: ({node, ...props}) => <ol className="list-decimal list-inside space-y-1 mb-3 text-sm text-gray-700" {...props} />,
                              li: ({node, ...props}) => <li className="ml-2" {...props} />,

                              // Customize strong/bold
                              strong: ({node, ...props}) => <strong className="font-semibold text-gray-900" {...props} />,

                              // Customize code blocks
                              code: ({node, inline, ...props}) =>
                                inline ? (
                                  <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-primary-700" {...props} />
                                ) : (
                                  <code className="block bg-gray-100 p-3 rounded-lg text-xs font-mono overflow-x-auto" {...props} />
                                ),

                              // Customize tables
                              table: ({node, ...props}) => (
                                <div className="overflow-x-auto mb-4">
                                  <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg" {...props} />
                                </div>
                              ),
                              thead: ({node, ...props}) => <thead className="bg-gray-50" {...props} />,
                              tbody: ({node, ...props}) => <tbody className="bg-white divide-y divide-gray-200" {...props} />,
                              tr: ({node, ...props}) => <tr {...props} />,
                              th: ({node, ...props}) => <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider" {...props} />,
                              td: ({node, ...props}) => <td className="px-4 py-2 text-sm text-gray-700" {...props} />,

                              // Customize blockquotes
                              blockquote: ({node, ...props}) => (
                                <blockquote className="border-l-4 border-primary-500 pl-4 py-2 italic text-gray-700 bg-primary-50 rounded-r" {...props} />
                              ),
                            }}
                          >
                            {insight.full_content || insight.description}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-600 line-clamp-3 leading-relaxed">
                          {stripMarkdown(insight.description || insight.full_content || '').substring(0, 250)}
                          {(insight.description || insight.full_content || '').length > 250 ? '...' : ''}
                        </p>
                      )}
                    </div>

                    {/* Key Metrics Badges (shown when expanded) */}
                    {isExpanded && keyMetrics.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {keyMetrics.map((metric, i) => (
                          <div key={i} className="bg-primary-50 border border-primary-200 rounded-lg px-3 py-2">
                            <div className="text-xs text-primary-600 font-medium">{metric.label}</div>
                            <div className="text-lg font-bold text-primary-900">{metric.value}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Data Summary (shown when collapsed and data exists) */}
                    {!isExpanded && insight.data && Object.keys(insight.data).length > 0 && (
                      <div className="bg-white rounded-lg p-3 mt-3 border border-gray-100">
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                          {Object.entries(insight.data).slice(0, 4).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-gray-500 block mb-0.5">
                                {key.replace(/_/g, ' ').charAt(0).toUpperCase() + key.replace(/_/g, ' ').slice(1)}
                              </span>
                              <span className="font-semibold text-gray-900 block">
                                {typeof value === 'number'
                                  ? value.toLocaleString()
                                  : Array.isArray(value)
                                  ? `${value.length} items`
                                  : String(value).substring(0, 30)
                                }
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Source Tag */}
                    {insight.source && (
                      <div className="mt-3 flex items-center gap-2">
                        <span className="text-xs text-gray-400">
                          Source: <span className="font-medium text-gray-600">{insight.source}</span>
                        </span>
                        {insight.type && (
                          <span className="text-xs text-gray-400">•</span>
                        )}
                        {insight.type && (
                          <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                            {insight.type.replace(/_/g, ' ')}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}

          {/* Show more indicator if there are more than 10 insights */}
          {insights.length > 10 && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-500">
                Showing 10 of {insights.length} insights
              </p>
            </div>
          )}
        </div>
        )}
      </div>
    </div>
  )
}

export default InsightsDashboard
