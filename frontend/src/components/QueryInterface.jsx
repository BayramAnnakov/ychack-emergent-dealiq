import React, { useState } from 'react'
import { Send, Sparkles, TrendingUp, Target, Users, Loader } from 'lucide-react'
import toast from 'react-hot-toast'
import { analyzeData, predictOutcomes, testHypothesis, analyzeDataStreaming } from '../services/api'

function QueryInterface({ fileId, onQueryResult, isLoading, setIsLoading }) {
  const [query, setQuery] = useState('')
  const [queryType, setQueryType] = useState('analyze')
  const [streamingStatus, setStreamingStatus] = useState('')
  const [streamingProgress, setStreamingProgress] = useState(0)
  const [progressLog, setProgressLog] = useState([])
  const [showConfetti, setShowConfetti] = useState(false)
  const [executionPhases, setExecutionPhases] = useState([
    { name: 'Upload', status: 'complete', icon: '🚀' },
    { name: 'Analyze', status: 'pending', icon: '🔍' },
    { name: 'Generate', status: 'pending', icon: '💡' },
    { name: 'Deliver', status: 'pending', icon: '✅' }
  ])

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
    setStreamingStatus('Initializing Claude analysis...')
    setStreamingProgress(0)
    setProgressLog([])
    setShowConfetti(false)
    setExecutionPhases([
      { name: 'Upload', status: 'complete', icon: '🚀' },
      { name: 'Analyze', status: 'active', icon: '🔍' },
      { name: 'Generate', status: 'pending', icon: '💡' },
      { name: 'Deliver', status: 'pending', icon: '✅' }
    ])

    try {
      // Use streaming for analyze type
      if (queryType === 'analyze') {
        const result = await analyzeDataStreaming(fileId, query, 'pipeline_analysis', {
          onStatus: (data) => {
            setStreamingStatus(data.message)
            setStreamingProgress(data.progress || 0)
            setProgressLog(prev => [...prev, { 
              message: data.message, 
              time: new Date().toLocaleTimeString(),
              progress: data.progress || 0
            }])
            
            // Update phases
            const prog = data.progress || 0
            setExecutionPhases(phases => {
              const newPhases = [...phases]
              if (prog >= 30 && prog < 70) {
                newPhases[1].status = 'complete'
                newPhases[2].status = 'active'
              } else if (prog >= 70) {
                newPhases[2].status = 'complete'
                newPhases[3].status = 'active'
              }
              return newPhases
            })
          },
          onPartial: (data) => {
            setStreamingStatus(data.message || 'Analyzing...')
            setStreamingProgress(data.progress || 50)
            setProgressLog(prev => [...prev, { 
              message: data.message || 'Analyzing...', 
              time: new Date().toLocaleTimeString(),
              progress: data.progress || 50
            }])
          },
          onTool: (data) => {
            setStreamingStatus(data.message)
            setStreamingProgress(data.progress || streamingProgress)
            setProgressLog(prev => [...prev, { 
              message: data.message, 
              time: new Date().toLocaleTimeString(),
              progress: data.progress || streamingProgress
            }])
          },
          onComplete: (data) => {
            setExecutionPhases(phases => phases.map(p => ({ ...p, status: 'complete' })))
            setShowConfetti(true)
            
            onQueryResult(data)
            toast.success(`Analysis complete! (${data.processing_time?.toFixed(1)}s)`)
            setStreamingStatus('')
            setStreamingProgress(100)
            
            setTimeout(() => {
              setShowConfetti(false)
            }, 3000)
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
    <>
      {/* Progress Modal - Similar to Professional Reports */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          {/* Confetti Effect */}
          {showConfetti && (
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              {[...Array(50)].map((_, i) => (
                <div
                  key={i}
                  className="absolute animate-ping"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `${Math.random() * 100}%`,
                    animationDelay: `${Math.random() * 0.5}s`,
                    fontSize: `${Math.random() * 20 + 20}px`
                  }}
                >
                  {['🎉', '✨', '🎊', '⭐', '💡'][Math.floor(Math.random() * 5)]}
                </div>
              ))}
            </div>
          )}
          
          <div className="bg-white rounded-lg shadow-2xl p-8 max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <Loader className="h-8 w-8 text-blue-600 animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Analyzing Your CRM Data
              </h2>
              <p className="text-gray-600 mb-3">
                Claude is generating AI-powered insights...
              </p>
            </div>

            {/* Execution Timeline */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                {executionPhases.map((phase, idx) => (
                  <React.Fragment key={phase.name}>
                    <div className="flex flex-col items-center">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-xl mb-2 transition-all duration-300 ${
                        phase.status === 'complete' 
                          ? 'bg-green-500 text-white scale-110 shadow-lg' 
                          : phase.status === 'active'
                          ? 'bg-blue-500 text-white animate-pulse shadow-md'
                          : 'bg-gray-200 text-gray-400'
                      }`}>
                        {phase.icon}
                      </div>
                      <span className={`text-xs font-medium ${
                        phase.status === 'complete' 
                          ? 'text-green-700' 
                          : phase.status === 'active'
                          ? 'text-blue-700'
                          : 'text-gray-500'
                      }`}>
                        {phase.name}
                      </span>
                    </div>
                    {idx < executionPhases.length - 1 && (
                      <div className={`flex-1 h-1 mx-2 rounded transition-all duration-500 ${
                        executionPhases[idx + 1].status !== 'pending' 
                          ? 'bg-gradient-to-r from-green-400 to-green-500' 
                          : 'bg-gray-200'
                      }`} />
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="bg-gray-200 rounded-full h-4 overflow-hidden shadow-inner">
                <div
                  className="bg-gradient-to-r from-blue-500 via-blue-600 to-purple-600 h-full transition-all duration-300 flex items-center justify-end"
                  style={{ width: `${streamingProgress}%` }}
                >
                  <span className="text-white text-xs font-bold pr-2">
                    {streamingProgress}%
                  </span>
                </div>
              </div>
            </div>

            {/* Current Status */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <p className="text-sm font-medium text-gray-900">{streamingStatus}</p>
            </div>

            {/* Activity Log */}
            <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-y-auto min-h-[200px] max-h-[350px] border border-gray-200">
              <h3 className="text-xs font-semibold text-gray-700 mb-3 sticky top-0 bg-gray-50">Activity Log:</h3>
              <div className="space-y-2">
                {progressLog.slice(-15).map((entry, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-xs">
                    <span className="text-gray-400 flex-shrink-0 font-mono">{entry.time}</span>
                    <span className="text-gray-700 flex-1">{entry.message}</span>
                    <span className="text-gray-400 flex-shrink-0">{entry.progress}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Additional Info */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center text-xs">
                <div>
                  <p className="text-gray-500">Analysis Type</p>
                  <p className="font-semibold text-blue-600 capitalize">{queryType}</p>
                </div>
                <div>
                  <p className="text-gray-500">AI Model</p>
                  <p className="font-semibold text-purple-600">Claude Sonnet</p>
                </div>
                <div>
                  <p className="text-gray-500">Est. Time</p>
                  <p className="font-semibold text-gray-700">30-60s</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Query Interface Card */}
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

        {/* Removed old simple progress bar */}

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
    </>
  )
}

export default QueryInterface