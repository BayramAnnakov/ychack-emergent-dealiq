import React, { useState } from 'react'
import { Send, Sparkles, TrendingUp, Target, Users } from 'lucide-react'
import toast from 'react-hot-toast'
import { analyzeData, predictOutcomes, testHypothesis, analyzeDataStreaming } from '../services/api'

function QueryInterface({ fileId, onQueryResult, isLoading, setIsLoading }) {
  const [query, setQuery] = useState('')
  const [queryType, setQueryType] = useState('analyze')
  const [streamingStatus, setStreamingStatus] = useState('')
  const [streamingProgress, setStreamingProgress] = useState(0)

  const exampleQueries = [
    { icon: Sparkles, text: "What are my top opportunities?", type: "analyze" },
    { icon: TrendingUp, text: "Which deals will close this quarter?", type: "predict" },
    { icon: Target, text: "Do longer cycles mean bigger deals?", type: "hypothesis" },
    { icon: Users, text: "Who are my top performers?", type: "analyze" }
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      toast.error('Please enter a query')
      return
    }

    setIsLoading(true)
    setStreamingStatus('Initializing...')
    setStreamingProgress(0)

    try {
      // Use streaming for analyze type
      if (queryType === 'analyze') {
        const result = await analyzeDataStreaming(fileId, query, 'pipeline_analysis', {
          onStatus: (data) => {
            setStreamingStatus(data.message)
            setStreamingProgress(data.progress || 0)
          },
          onPartial: (data) => {
            // Use the message from the backend if available
            setStreamingStatus(data.message || 'Analyzing...')
            setStreamingProgress(data.progress || 50)
          },
          onTool: (data) => {
            setStreamingStatus(data.message)
            setStreamingProgress(data.progress || streamingProgress)
          },
          onComplete: (data) => {
            onQueryResult(data)
            toast.success(`Analysis complete! (${data.processing_time?.toFixed(1)}s)`)
            setStreamingStatus('')
            setStreamingProgress(100)
          },
          onError: (data) => {
            toast.error(data.message || 'Failed to analyze query')
            setStreamingStatus('')
            setStreamingProgress(0)
          }
        })
      } else if (queryType === 'predict') {
        const result = await predictOutcomes(fileId, 'deal_closure', query)
        onQueryResult(result)
        toast.success('Analysis complete!')
      } else if (queryType === 'hypothesis') {
        const result = await testHypothesis(fileId, query)
        onQueryResult(result)
        toast.success('Analysis complete!')
      }
    } catch (error) {
      toast.error(error.message || 'Failed to analyze query')
      setStreamingStatus('')
      setStreamingProgress(0)
    } finally {
      setIsLoading(false)
    }
  }

  const handleExampleClick = (example) => {
    setQuery(example.text)
    setQueryType(example.type)
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Ask Your Data</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Query Type
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setQueryType('analyze')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                queryType === 'analyze'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Analyze
            </button>
            <button
              type="button"
              onClick={() => setQueryType('predict')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                queryType === 'predict'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Predict
            </button>
            <button
              type="button"
              onClick={() => setQueryType('hypothesis')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                queryType === 'hypothesis'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Test
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Question
          </label>
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything about your sales data..."
              className="input min-h-[100px] pr-12"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="absolute bottom-2 right-2 p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

        {isLoading && streamingStatus && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-blue-700 font-medium">{streamingStatus}</span>
              <span className="text-xs text-blue-600">{streamingProgress}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${streamingProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        <div>
          <p className="text-xs font-medium text-gray-500 mb-2">Example queries:</p>
          <div className="space-y-2">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleExampleClick(example)}
                className="w-full text-left flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <example.icon className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-700">{example.text}</span>
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  )
}

export default QueryInterface