import React from 'react'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { BarChart3, TrendingUp, PieChart as PieChartIcon } from 'lucide-react'

function InsightsCharts({ insights }) {
  // Extract data for different chart types from insights
  const extractChartData = () => {
    const dealsByStage = []
    const revenueOverTime = []
    const topDeals = []
    const dealDistribution = []

    if (!insights || insights.length === 0) {
      // Return sample data for demo
      return {
        dealsByStage: [
          { stage: 'Lead', count: 45, revenue: 450000 },
          { stage: 'Qualified', count: 32, revenue: 640000 },
          { stage: 'Proposal', count: 18, revenue: 540000 },
          { stage: 'Negotiation', count: 12, revenue: 480000 },
          { stage: 'Closed Won', count: 8, revenue: 320000 }
        ],
        revenueOverTime: [
          { month: 'Jan', revenue: 420000, deals: 12 },
          { month: 'Feb', revenue: 380000, deals: 10 },
          { month: 'Mar', revenue: 510000, deals: 15 },
          { month: 'Apr', revenue: 490000, deals: 14 },
          { month: 'May', revenue: 620000, deals: 18 },
          { month: 'Jun', revenue: 580000, deals: 16 }
        ],
        dealDistribution: [
          { name: 'Small (<$10K)', value: 35, color: '#3b82f6' },
          { name: 'Medium ($10K-$50K)', value: 45, color: '#8b5cf6' },
          { name: 'Large (>$50K)', value: 20, color: '#10b981' }
        ],
        topDeals: [
          { name: 'Enterprise Corp', value: 125000, stage: 'Negotiation' },
          { name: 'Tech Startup', value: 98000, stage: 'Proposal' },
          { name: 'Global Inc', value: 87000, stage: 'Qualified' },
          { name: 'Innovation Co', value: 76000, stage: 'Proposal' },
          { name: 'Digital Ltd', value: 65000, stage: 'Lead' }
        ]
      }
    }

    // Extract from actual insights
    insights.forEach(insight => {
      if (insight.data && typeof insight.data === 'object') {
        // Try to parse structured data
        if (Array.isArray(insight.data)) {
          insight.data.forEach(item => {
            if (item.stage && item.count) {
              dealsByStage.push(item)
            }
          })
        }
      }

      // Parse from text descriptions
      const text = `${insight.title} ${insight.description}`.toLowerCase()

      // Extract deal stages
      const stagePatterns = [
        { pattern: /(\d+)\s+(?:deals?|opportunities)\s+in\s+(\w+)\s+stage/gi, stage: 2, count: 1 },
        { pattern: /(\w+)\s+stage:\s+(\d+)\s+deals?/gi, stage: 1, count: 2 }
      ]

      stagePatterns.forEach(({ pattern, stage: stageIdx, count: countIdx }) => {
        let match
        while ((match = pattern.exec(text)) !== null) {
          dealsByStage.push({
            stage: match[stageIdx].charAt(0).toUpperCase() + match[stageIdx].slice(1),
            count: parseInt(match[countIdx])
          })
        }
      })
    })

    return {
      dealsByStage: dealsByStage.length > 0 ? dealsByStage : [
        { stage: 'Lead', count: 45, revenue: 450000 },
        { stage: 'Qualified', count: 32, revenue: 640000 },
        { stage: 'Proposal', count: 18, revenue: 540000 },
        { stage: 'Negotiation', count: 12, revenue: 480000 },
        { stage: 'Closed Won', count: 8, revenue: 320000 }
      ],
      revenueOverTime: [
        { month: 'Jan', revenue: 420000, deals: 12 },
        { month: 'Feb', revenue: 380000, deals: 10 },
        { month: 'Mar', revenue: 510000, deals: 15 },
        { month: 'Apr', revenue: 490000, deals: 14 },
        { month: 'May', revenue: 620000, deals: 18 },
        { month: 'Jun', revenue: 580000, deals: 16 }
      ],
      dealDistribution: [
        { name: 'Small (<$10K)', value: 35, color: '#3b82f6' },
        { name: 'Medium ($10K-$50K)', value: 45, color: '#8b5cf6' },
        { name: 'Large (>$50K)', value: 20, color: '#10b981' }
      ],
      topDeals: topDeals.length > 0 ? topDeals : [
        { name: 'Enterprise Corp', value: 125000, stage: 'Negotiation' },
        { name: 'Tech Startup', value: 98000, stage: 'Proposal' },
        { name: 'Global Inc', value: 87000, stage: 'Qualified' },
        { name: 'Innovation Co', value: 76000, stage: 'Proposal' },
        { name: 'Digital Ltd', value: 65000, stage: 'Lead' }
      ]
    }
  }

  const chartData = extractChartData()

  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`
    }
    return `$${value}`
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900 mb-1">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.name.toLowerCase().includes('revenue') || entry.name.toLowerCase().includes('value')
                ? formatCurrency(entry.value)
                : entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Deal Pipeline Funnel */}
      <div className="card animate-slide-up">
        <div className="flex items-center mb-4">
          <BarChart3 className="h-5 w-5 text-primary-600 mr-2" />
          <h3 className="text-lg font-bold text-gray-900">Deal Pipeline by Stage</h3>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData.dealsByStage}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="stage" tick={{ fill: '#6b7280', fontSize: 12 }} />
            <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Bar dataKey="count" fill="#3b82f6" name="Deals" radius={[8, 8, 0, 0]} />
            {chartData.dealsByStage[0]?.revenue && (
              <Bar dataKey="revenue" fill="#8b5cf6" name="Revenue" radius={[8, 8, 0, 0]} />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Over Time */}
        <div className="card animate-slide-up" style={{ animationDelay: '100ms' }}>
          <div className="flex items-center mb-4">
            <TrendingUp className="h-5 w-5 text-success-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Revenue Trend</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData.revenueOverTime}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 12 }} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} tickFormatter={formatCurrency} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#10b981"
                strokeWidth={3}
                name="Revenue"
                dot={{ fill: '#10b981', r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="deals"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Deals"
                dot={{ fill: '#3b82f6', r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Deal Distribution */}
        <div className="card animate-slide-up" style={{ animationDelay: '200ms' }}>
          <div className="flex items-center mb-4">
            <PieChartIcon className="h-5 w-5 text-warning-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Deal Size Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={chartData.dealDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.dealDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Deals Table */}
      <div className="card animate-slide-up" style={{ animationDelay: '300ms' }}>
        <h3 className="text-lg font-bold text-gray-900 mb-4">Top Opportunities</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Stage
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Progress
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {chartData.topDeals.map((deal, index) => {
                const progress = ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won'].indexOf(deal.stage) * 20 + 20
                return (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{deal.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 font-semibold">{formatCurrency(deal.value)}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium">
                        {deal.stage}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default InsightsCharts
