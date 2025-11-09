import React, { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import FileUpload from './components/FileUpload'
import QueryInterface from './components/QueryInterface'
import InsightsDashboard from './components/InsightsDashboard'
import PipelineMetrics from './components/PipelineMetrics'
import BenchmarkInterface from './components/BenchmarkInterface'
import BenchmarkResults from './components/BenchmarkResults'

function App() {
  const [mode, setMode] = useState('crm') // 'crm' or 'benchmark'
  const [uploadedFile, setUploadedFile] = useState(null)
  const [insights, setInsights] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [benchmarkResult, setBenchmarkResult] = useState(null)

  const handleFileUpload = (fileData) => {
    setUploadedFile(fileData)
    // Quick insights are generated on upload
    if (fileData.stats) {
      setMetrics(fileData.stats)
    }
  }

  const handleQuerySubmit = async (queryResult) => {
    setInsights(queryResult.insights)
  }

  const handleModeChange = (newMode) => {
    setMode(newMode)
    // Clear results when switching modes
    if (newMode === 'benchmark') {
      setBenchmarkResult(null)
    }
  }

  const handleBenchmarkResultReady = (result) => {
    setBenchmarkResult(result)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Toaster position="top-right" />
      <Header mode={mode} onModeChange={handleModeChange} />

      <main className="container mx-auto px-4 py-8">
        {mode === 'crm' ? (
          /* CRM Analysis Mode */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Upload and Query */}
            <div className="lg:col-span-1 space-y-6">
              <FileUpload onUploadSuccess={handleFileUpload} />

              {uploadedFile && (
                <QueryInterface
                  fileId={uploadedFile.file_id}
                  onQueryResult={handleQuerySubmit}
                  isLoading={isLoading}
                  setIsLoading={setIsLoading}
                />
              )}
            </div>

            {/* Right Column - Results */}
            <div className="lg:col-span-2 space-y-6">
              {metrics && (
                <PipelineMetrics metrics={metrics} />
              )}

              {insights && (
                <InsightsDashboard insights={insights} isLoading={isLoading} />
              )}

              {!uploadedFile && !insights && (
                <div className="card text-center py-16">
                  <svg className="mx-auto h-24 w-24 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <h3 className="mt-4 text-lg font-medium text-gray-900">No data uploaded</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Upload a CRM export to get started with AI-powered insights
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Benchmark Mode */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Task Selection */}
            <div className="lg:col-span-1">
              <BenchmarkInterface
                onResultReady={handleBenchmarkResultReady}
              />
            </div>

            {/* Right Column - Results */}
            <div className="lg:col-span-2">
              {benchmarkResult ? (
                <BenchmarkResults result={benchmarkResult} />
              ) : (
                <div className="card text-center py-16">
                  <svg className="mx-auto h-24 w-24 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="mt-4 text-lg font-medium text-gray-900">Ready to Generate Professional Reports</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Execute a benchmark task to generate validated Excel reports with formulas
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App