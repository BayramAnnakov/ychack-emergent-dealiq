import React from 'react'
import { DollarSign, TrendingUp, Users, Clock, BarChart3, PieChart } from 'lucide-react'

function PipelineMetrics({ metrics }) {
  if (!metrics) return null

  const formatCurrency = (value) => {
    if (typeof value !== 'number') return '$0'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatNumber = (value) => {
    if (typeof value !== 'number') return '0'
    return value.toLocaleString()
  }

  const metricCards = [
    {
      icon: DollarSign,
      label: 'Total Pipeline',
      value: formatCurrency(metrics.total_pipeline_value || 0),
      color: 'text-success-600 bg-success-50'
    },
    {
      icon: BarChart3,
      label: 'Average Deal Size',
      value: formatCurrency(metrics.average_deal_size || 0),
      color: 'text-primary-600 bg-primary-50'
    },
    {
      icon: Users,
      label: 'Total Deals',
      value: formatNumber(metrics.total_rows || 0),
      color: 'text-purple-600 bg-purple-50'
    },
    {
      icon: Clock,
      label: 'Avg Sales Cycle',
      value: `${Math.round(metrics.average_sales_cycle || 0)} days`,
      color: 'text-orange-600 bg-orange-50'
    }
  ]

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4 flex items-center">
        <PieChart className="h-5 w-5 mr-2 text-primary-600" />
        Pipeline Overview
      </h2>

      <div className="grid grid-cols-2 gap-4">
        {metricCards.map((metric, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className={`p-2 rounded-lg ${metric.color}`}>
                <metric.icon className="h-4 w-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {metric.value}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              {metric.label}
            </div>
          </div>
        ))}
      </div>

      {metrics.deals_by_stage && Object.keys(metrics.deals_by_stage).length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Deals by Stage</h3>
          <div className="space-y-2">
            {Object.entries(metrics.deals_by_stage)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 5)
              .map(([stage, count]) => {
                const percentage = (count / metrics.total_rows) * 100
                return (
                  <div key={stage} className="flex items-center">
                    <div className="flex-1">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-700">{stage}</span>
                        <span className="text-gray-900 font-medium">{count}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      )}

      {metrics.win_rate !== undefined && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Win Rate</span>
            <span className="text-lg font-bold text-gray-900">
              {(metrics.win_rate * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className="bg-success-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${metrics.win_rate * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default PipelineMetrics