import React, { useState } from 'react'
import { Target, AlertTriangle, Lightbulb, TrendingUp, ChevronDown, ChevronUp, CheckCircle2, Clock, DollarSign, Users } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function ActionableInsights({ insights }) {
  const [expandedSections, setExpandedSections] = useState({})
  const [expandedOpportunities, setExpandedOpportunities] = useState({})

  // Enhanced opportunity parser
  const parseOpportunities = (opportunityInsights) => {
    if (!opportunityInsights || opportunityInsights.length === 0) return []

    const opportunities = []

    opportunityInsights.forEach(insight => {
      const content = insight.content || insight.full_content || insight.description || ''
      const lines = content.split('\n')

      lines.forEach((line, idx) => {
        const trimmed = line.trim()

        // Pattern 1: Markdown tables | Rank | Name | Value | Stage | Owner |
        const tableMatch = trimmed.match(/^\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|/)
        if (tableMatch) {
          const [, rank, name, value, stage, owner] = tableMatch

          // Skip header rows
          if (!name.includes('Deal') && !name.includes('Name') && !name.includes('---')) {
            const dealName = name.trim()
            const dealValue = value.trim().replace(/[\$,]/g, '')

            if (dealName && dealValue && !isNaN(parseFloat(dealValue))) {
              opportunities.push({
                rank: rank.trim(),
                name: dealName,
                value: `$${parseFloat(dealValue).toLocaleString()}`,
                stage: stage?.trim() || 'Unknown',
                owner: owner?.trim() || 'Unassigned',
                context: extractDealContext(content, dealName),
                why: extractWhy(content, dealName),
                risk: extractRisk(content, dealName),
                nextSteps: extractNextSteps(content, dealName)
              })
            }
          }
        }

        // Pattern 2: "1. CompanyName - $Amount (Stage)"
        const listMatch = trimmed.match(/^(\d+)\.\s*(.+?)\s*[-–]\s*\$?([\d,]+)\s*(?:\((.+?)\))?/)
        if (listMatch) {
          const [, rank, name, value, stage] = listMatch
          opportunities.push({
            rank,
            name: name.trim(),
            value: `$${parseFloat(value.replace(/,/g, '')).toLocaleString()}`,
            stage: stage || 'Unknown',
            context: extractDealContext(content, name),
            why: extractWhy(content, name),
            risk: extractRisk(content, name),
            nextSteps: extractNextSteps(content, name)
          })
        }

        // Pattern 3: "CompanyName: $Amount"
        const simpleMatch = trimmed.match(/^([A-Z][A-Za-z\s&]+?):\s*\$?([\d,]+)/)
        if (simpleMatch && !trimmed.includes('|')) {
          const [, name, value] = simpleMatch
          if (!name.includes('Total') && !name.includes('Average')) {
            opportunities.push({
              name: name.trim(),
              value: `$${parseFloat(value.replace(/,/g, '')).toLocaleString()}`,
              context: lines[idx + 1] || '',
              why: extractWhy(content, name),
              risk: extractRisk(content, name),
              nextSteps: extractNextSteps(content, name)
            })
          }
        }
      })
    })

    // Remove duplicates and sort by value
    const unique = opportunities.reduce((acc, opp) => {
      if (!acc.find(o => o.name === opp.name)) {
        acc.push(opp)
      }
      return acc
    }, [])

    return unique
      .sort((a, b) => {
        const aVal = parseFloat(a.value.replace(/[\$,]/g, ''))
        const bVal = parseFloat(b.value.replace(/[\$,]/g, ''))
        return bVal - aVal
      })
      .slice(0, 5)
  }

  // Extract WHY this deal matters
  const extractWhy = (content, dealName) => {
    const lines = content.split('\n')
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(dealName)) {
        const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 3)).join(' ')

        if (context.match(/(?:high probability|likely to close|strong signal|qualified|engaged|ready to buy)/i)) {
          return '🎯 High probability to close'
        }
        if (context.match(/(?:largest|biggest|high[- ]value|enterprise|strategic)/i)) {
          return '💰 High-value strategic deal'
        }
        if (context.match(/(?:urgent|immediate|time[- ]sensitive|deadline|q[1-4]|quarter)/i)) {
          return '⏰ Time-sensitive opportunity'
        }
        if (context.match(/(?:existing|current|upsell|expansion|renewal)/i)) {
          return '🤝 Expansion opportunity'
        }
      }
    }
    return null
  }

  // Extract RISK factors
  const extractRisk = (content, dealName) => {
    const lines = content.split('\n')
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(dealName)) {
        const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 3)).join(' ')

        if (context.match(/(?:stalled|stuck|no activity|delayed|slow)/i)) {
          return '⚠️ Deal momentum stalled'
        }
        if (context.match(/(?:competitor|competitive|evaluation|comparing)/i)) {
          return '🏁 Active competition'
        }
        if (context.match(/(?:budget|pricing|cost|expensive)/i)) {
          return '💸 Budget concerns'
        }
        if (context.match(/(?:stakeholder|decision[- ]maker|approval|champion)/i)) {
          return '👥 Missing key stakeholders'
        }
      }
    }
    return null
  }

  // Extract NEXT STEPS
  const extractNextSteps = (content, dealName) => {
    const lines = content.split('\n')
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(dealName)) {
        const context = lines.slice(i, Math.min(lines.length, i + 5)).join(' ')

        if (context.match(/(?:follow[- ]up|reach out|contact|call|email|schedule)/i)) {
          return 'Follow up with decision maker'
        }
        if (context.match(/(?:demo|presentation|show|showcase)/i)) {
          return 'Schedule product demo'
        }
        if (context.match(/(?:proposal|quote|pricing|contract)/i)) {
          return 'Send proposal/pricing'
        }
        if (context.match(/(?:close|sign|contract|agreement|commit)/i)) {
          return 'Push for commitment'
        }
      }
    }
    return 'Review and prioritize'
  }

  // Extract deal context
  const extractDealContext = (content, dealName) => {
    const lines = content.split('\n')
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(dealName)) {
        const line = lines[i].replace(/[|#*-]/g, '').trim()
        if (line.length > dealName.length + 10) {
          return line.substring(0, 200)
        }
        if (lines[i + 1]) {
          return lines[i + 1].replace(/[|#*-]/g, '').trim().substring(0, 200)
        }
      }
    }
    return ''
  }

  // Enhanced problem parser
  const parseProblems = (problemInsights) => {
    if (!problemInsights || problemInsights.length === 0) return []

    const problems = []

    problemInsights.forEach(insight => {
      const content = insight.content || insight.full_content || insight.description || ''
      const title = insight.title || ''
      const lines = content.split('\n').filter(l => l.trim())

      const problemType = detectProblemType(title, content)
      const severity = detectSeverity(content)
      const affectedDeals = extractAffectedDeals(content)
      const suggestion = extractSuggestion(content, problemType)
      const impact = extractImpact(content)

      problems.push({
        title: title.replace(/[#*]/g, '').trim(),
        type: problemType,
        severity,
        summary: lines[0]?.replace(/[#*-]/g, '').trim().substring(0, 150) || '',
        affectedDeals,
        suggestion,
        impact,
        fullContent: content
      })
    })

    return problems.sort((a, b) => {
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
      return severityOrder[a.severity] - severityOrder[b.severity]
    })
  }

  const detectProblemType = (title, content) => {
    const text = `${title} ${content}`.toLowerCase()

    if (text.match(/bottleneck|stuck|stalled|blocked/)) return 'bottleneck'
    if (text.match(/conversion|win rate|loss|lost/)) return 'conversion'
    if (text.match(/pipeline|velocity|cycle|time/)) return 'velocity'
    if (text.match(/forecast|quota|target/)) return 'forecast'
    if (text.match(/churn|retention|renewal/)) return 'churn'

    return 'general'
  }

  const detectSeverity = (content) => {
    const text = content.toLowerCase()

    if (text.match(/critical|urgent|immediate|severe/)) return 'critical'
    if (text.match(/high|significant|major|important/)) return 'high'
    if (text.match(/moderate|medium/)) return 'medium'

    return 'low'
  }

  const extractAffectedDeals = (content) => {
    const countMatch = content.match(/(\d+)\s+deals?/i)
    if (countMatch) {
      return `${countMatch[1]} deals affected`
    }

    const percentMatch = content.match(/(\d+)%/i)
    if (percentMatch) {
      return `${percentMatch[1]}% of pipeline`
    }

    return null
  }

  const extractSuggestion = (content, problemType) => {
    const lines = content.split('\n')

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].toLowerCase()
      if (line.includes('recommend') || line.includes('suggest') || line.includes('should') || line.includes('action')) {
        const nextLines = lines.slice(i + 1, i + 3).filter(l => l.trim())
        if (nextLines.length > 0) {
          return nextLines[0].replace(/[#*-]/g, '').trim().substring(0, 150)
        }
      }
    }

    // Type-based suggestions
    const suggestions = {
      bottleneck: 'Streamline process, assign specialist, or automate workflow',
      conversion: 'Strengthen qualification criteria and improve sales training',
      velocity: 'Implement automated follow-up cadence and reduce approval steps',
      forecast: 'Review pipeline health and adjust sales strategy',
      churn: 'Increase customer engagement and identify at-risk accounts early'
    }

    return suggestions[problemType] || 'Review and address root cause'
  }

  const extractImpact = (content) => {
    const dollarMatch = content.match(/\$?([\d,]+(?:,\d{3})*(?:\.\d{2})?)\s*(?:in\s+)?(?:revenue|value|pipeline)?/i)
    if (dollarMatch) {
      const amount = parseFloat(dollarMatch[1].replace(/,/g, ''))
      if (amount > 1000) {
        return `$${amount.toLocaleString()} at risk`
      }
    }

    return null
  }

  // Categorize insights
  const categorizeInsights = () => {
    const categories = {
      opportunities: [],
      problems: [],
      recommendations: []
    }

    if (!insights || insights.length === 0) return categories

    insights.forEach(insight => {
      const title = (insight.title || '').toLowerCase()
      const content = insight.full_content || insight.description || ''

      if (title.includes('opportunit') || title.includes('top') || title.includes('deal') || title.includes('key deal')) {
        categories.opportunities.push({ ...insight, content })
      } else if (title.includes('bottleneck') || title.includes('issue') || title.includes('problem') || title.includes('risk') || title.includes('critical')) {
        categories.problems.push({ ...insight, content })
      } else {
        categories.recommendations.push({ ...insight, content })
      }
    })

    return categories
  }

  const categories = categorizeInsights()
  const opportunities = parseOpportunities(categories.opportunities)
  const problems = parseProblems(categories.problems)

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const toggleOpportunity = (index) => {
    setExpandedOpportunities(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'border-error-500 bg-gradient-to-r from-error-50 to-white',
      high: 'border-warning-500 bg-gradient-to-r from-warning-50 to-white',
      medium: 'border-warning-300 bg-gradient-to-r from-warning-50 to-white',
      low: 'border-gray-300 bg-gradient-to-r from-gray-50 to-white'
    }
    return colors[severity] || colors.low
  }

  const getProblemIcon = (type) => {
    const icons = {
      bottleneck: '🚧',
      conversion: '📉',
      velocity: '⏱️',
      forecast: '📊',
      churn: '🔄',
      general: '⚠️'
    }
    return icons[type] || '⚠️'
  }

  return (
    <div className="space-y-4">
      {/* Top Opportunities */}
      {opportunities.length > 0 && (
        <div className="card border-l-4 border-l-primary-500 animate-slide-up">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="bg-primary-100 p-3 rounded-xl">
                <Target className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">🎯 Your Top Opportunities</h3>
                <p className="text-sm text-gray-600">Prioritize these deals for maximum impact</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {opportunities.map((opp, index) => (
              <div
                key={index}
                className="bg-gradient-to-r from-primary-50 to-white rounded-lg border border-primary-200 hover:border-primary-300 transition-all overflow-hidden"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary-600 text-white text-sm font-bold">
                          {opp.rank || index + 1}
                        </span>
                        <span className="text-lg font-bold text-gray-900">{opp.name}</span>
                        <span className="text-xl font-bold text-primary-600">{opp.value}</span>
                        {opp.stage && (
                          <span className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded-full font-medium">
                            {opp.stage}
                          </span>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-3 text-sm">
                        {opp.why && (
                          <span className="flex items-center gap-1 text-success-700">
                            <CheckCircle2 className="h-4 w-4" />
                            {opp.why}
                          </span>
                        )}
                        {opp.risk && (
                          <span className="flex items-center gap-1 text-warning-700">
                            <AlertTriangle className="h-4 w-4" />
                            {opp.risk}
                          </span>
                        )}
                        {opp.nextSteps && (
                          <span className="flex items-center gap-1 text-primary-700">
                            <Clock className="h-4 w-4" />
                            {opp.nextSteps}
                          </span>
                        )}
                        {opp.owner && (
                          <span className="flex items-center gap-1 text-gray-600">
                            <Users className="h-4 w-4" />
                            {opp.owner}
                          </span>
                        )}
                      </div>
                    </div>

                    {opp.context && (
                      <button
                        onClick={() => toggleOpportunity(index)}
                        className="ml-3 text-gray-400 hover:text-primary-600 transition-colors"
                      >
                        {expandedOpportunities[index] ? (
                          <ChevronUp className="h-5 w-5" />
                        ) : (
                          <ChevronDown className="h-5 w-5" />
                        )}
                      </button>
                    )}
                  </div>

                  {expandedOpportunities[index] && opp.context && (
                    <div className="mt-3 pt-3 border-t border-primary-100">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {opp.context}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Critical Issues/Problems */}
      {problems.length > 0 && (
        <div className="card border-l-4 border-l-warning-500 animate-slide-up" style={{ animationDelay: '100ms' }}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="bg-warning-100 p-3 rounded-xl">
                <AlertTriangle className="h-6 w-6 text-warning-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">⚠️ Critical Issues Identified</h3>
                <p className="text-sm text-gray-600">Address these blockers to unblock revenue</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {problems.map((problem, index) => (
              <div
                key={index}
                className={`rounded-lg border-l-4 p-4 ${getSeverityColor(problem.severity)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg">{getProblemIcon(problem.type)}</span>
                      <h4 className="font-semibold text-gray-900">{problem.title}</h4>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        problem.severity === 'critical' ? 'bg-error-100 text-error-700' :
                        problem.severity === 'high' ? 'bg-warning-100 text-warning-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {problem.severity.toUpperCase()}
                      </span>
                    </div>

                    <p className="text-sm text-gray-700 mb-2">{problem.summary}</p>

                    <div className="flex flex-wrap gap-3 text-sm">
                      {problem.affectedDeals && (
                        <span className="flex items-center gap-1 text-gray-600">
                          <DollarSign className="h-4 w-4" />
                          {problem.affectedDeals}
                        </span>
                      )}
                      {problem.impact && (
                        <span className="flex items-center gap-1 text-error-600 font-semibold">
                          <AlertTriangle className="h-4 w-4" />
                          {problem.impact}
                        </span>
                      )}
                    </div>

                    {problem.suggestion && (
                      <div className="mt-3 p-3 bg-success-50 border border-success-200 rounded-lg">
                        <div className="flex items-start gap-2">
                          <Lightbulb className="h-4 w-4 text-success-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-xs font-semibold text-success-900 mb-1">Suggested Fix:</p>
                            <p className="text-sm text-success-800">{problem.suggestion}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Recommendations */}
      {categories.recommendations.length > 0 && (
        <div className="card border-l-4 border-l-success-500 animate-slide-up" style={{ animationDelay: '200ms' }}>
          <button
            onClick={() => toggleSection('recommendations')}
            className="w-full flex items-start justify-between mb-4"
          >
            <div className="flex items-center gap-3">
              <div className="bg-success-100 p-3 rounded-xl">
                <Lightbulb className="h-6 w-6 text-success-600" />
              </div>
              <div className="text-left">
                <h3 className="text-xl font-bold text-gray-900">💡 Strategic Recommendations</h3>
                <p className="text-sm text-gray-600">AI-powered insights to optimize your sales process</p>
              </div>
            </div>
            {expandedSections.recommendations ? (
              <ChevronUp className="h-5 w-5 text-gray-400" />
            ) : (
              <ChevronDown className="h-5 w-5 text-gray-400" />
            )}
          </button>

          {expandedSections.recommendations && (
            <div className="space-y-4 mt-4">
              {categories.recommendations.map((rec, index) => (
                <div key={index} className="bg-gradient-to-r from-success-50 to-white p-4 rounded-lg border border-success-100">
                  <h4 className="font-semibold text-gray-900 mb-2">{rec.title}</h4>
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {rec.content}
                    </ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Fallback */}
      {opportunities.length === 0 && problems.length === 0 && categories.recommendations.length === 0 && insights && insights.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <Lightbulb className="h-6 w-6 text-primary-600" />
            <h3 className="text-xl font-bold text-gray-900">AI Analysis</h3>
          </div>
          <div className="space-y-4">
            {insights.slice(0, 3).map((insight, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">{insight.title}</h4>
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {insight.full_content || insight.description}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ActionableInsights
