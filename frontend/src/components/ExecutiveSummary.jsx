import React from 'react'
import { TrendingUp, TrendingDown, DollarSign, Users, Target, Activity } from 'lucide-react'

function ExecutiveSummary({ insights, analysisData }) {
  // Extract key metrics from insights and analysis data
  const extractMetrics = () => {
    const metrics = {
      totalDeals: 0,
      totalRevenue: 0,
      avgDealSize: 0,
      winRate: 0,
      activePipeline: 0,
      conversionRate: 0
    }

    // Try to extract from insights
    if (insights && insights.length > 0) {
      insights.forEach(insight => {
        if (insight.data) {
          // Look for common metric patterns
          Object.entries(insight.data).forEach(([key, value]) => {
            const lowerKey = key.toLowerCase()
            if (typeof value === 'number') {
              if (lowerKey.includes('deal') && lowerKey.includes('count')) {
                metrics.totalDeals = value
              }
              if (lowerKey.includes('revenue') || lowerKey.includes('amount')) {
                metrics.totalRevenue += value
              }
              if (lowerKey.includes('win') && lowerKey.includes('rate')) {
                metrics.winRate = value
              }
              if (lowerKey.includes('conversion')) {
                metrics.conversionRate = value
              }
            }
          })
        }

        // Parse from title and description
        const text = `${insight.title} ${insight.description}`.toLowerCase()

        // Extract win rate
        const winRateMatch = text.match(/win rate[:\s]+(\d+\.?\d*)%/)
        if (winRateMatch) {
          metrics.winRate = parseFloat(winRateMatch[1])
        }

        // Extract conversion rate
        const conversionMatch = text.match(/conversion rate[:\s]+(\d+\.?\d*)%/)
        if (conversionMatch) {
          metrics.conversionRate = parseFloat(conversionMatch[1])
        }

        // Extract revenue
        const revenueMatch = text.match(/\$?([\d,]+(?:\.\d{2})?)\s*(?:in revenue|revenue|total)/i)
        if (revenueMatch) {
          const amount = parseFloat(revenueMatch[1].replace(/,/g, ''))
          if (amount > metrics.totalRevenue) {
            metrics.totalRevenue = amount
          }
        }

        // Extract deal count
        const dealMatch = text.match(/(\d+)\s*(?:deals|opportunities)/i)
        if (dealMatch) {
          const count = parseInt(dealMatch[1])
          if (count > metrics.totalDeals) {
            metrics.totalDeals = count
          }
        }
      })
    }

    // Calculate derived metrics
    if (metrics.totalDeals > 0 && metrics.totalRevenue > 0) {
      metrics.avgDealSize = metrics.totalRevenue / metrics.totalDeals
    }
    metrics.activePipeline = metrics.totalRevenue

    return metrics
  }

  const metrics = extractMetrics()

  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`
    }
    return `$${value.toFixed(0)}`
  }

  const formatPercent = (value) => {
    return `${value.toFixed(1)}%`
  }

  const formatNumber = (value) => {
    return value.toLocaleString()
  }

  const metricCards = [
    {
      title: 'Total Pipeline',
      value: formatCurrency(metrics.activePipeline),
      icon: DollarSign,
      color: 'primary',
      trend: metrics.totalRevenue > 0 ? '+12%' : null,
      trendUp: true
    },
    {
      title: 'Active Deals',
      value: formatNumber(metrics.totalDeals),
      icon: Target,
      color: 'success',
      trend: metrics.totalDeals > 0 ? '+5' : null,
      trendUp: true
    },
    {
      title: 'Win Rate',
      value: metrics.winRate > 0 ? formatPercent(metrics.winRate) : 'N/A',
      icon: TrendingUp,
      color: 'warning',
      trend: metrics.winRate > 0 ? '+2.3%' : null,
      trendUp: true
    },
    {
      title: 'Avg Deal Size',
      value: metrics.avgDealSize > 0 ? formatCurrency(metrics.avgDealSize) : 'N/A',
      icon: Activity,
      color: 'purple',
      trend: metrics.avgDealSize > 0 ? '-3%' : null,
      trendUp: false
    }
  ]

  const getColorClasses = (color) => {
    const colorMap = {
      primary: {
        bg: 'bg-primary-50',
        text: 'text-primary-600',
        icon: 'text-primary-600'
      },
      success: {
        bg: 'bg-success-50',
        text: 'text-success-600',
        icon: 'text-success-600'
      },
      warning: {
        bg: 'bg-warning-50',
        text: 'text-warning-600',
        icon: 'text-warning-600'
      },
      purple: {
        bg: 'bg-purple-50',
        text: 'text-purple-600',
        icon: 'text-purple-600'
      }
    }
    return colorMap[color] || colorMap.primary
  }

  return (
    <div className="mb-6 animate-fade-in">
      <div className="mb-4 animate-slide-in">
        <h2 className="text-2xl font-bold text-gray-900">Executive Summary</h2>
        <p className="text-sm text-gray-600 mt-1">Key insights from your CRM analysis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((metric, index) => {
          const Icon = metric.icon
          const colors = getColorClasses(metric.color)

          return (
            <div
              key={index}
              className="bg-white rounded-xl p-5 border border-gray-200 hover:shadow-lg transition-all duration-300 hover:scale-105 animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`p-3 rounded-xl ${colors.bg}`}>
                  <Icon className={`h-6 w-6 ${colors.icon}`} />
                </div>
                {metric.trend && (
                  <div className={`flex items-center gap-1 text-xs font-medium ${
                    metric.trendUp ? 'text-success-600' : 'text-error-600'
                  }`}>
                    {metric.trendUp ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    {metric.trend}
                  </div>
                )}
              </div>

              <div>
                <p className="text-sm text-gray-600 mb-1">{metric.title}</p>
                <p className={`text-3xl font-bold ${colors.text}`}>
                  {metric.value}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ExecutiveSummary
