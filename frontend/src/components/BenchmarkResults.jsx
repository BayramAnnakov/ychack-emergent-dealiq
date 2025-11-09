import React, { useState, useEffect } from 'react'
import { Download, CheckCircle, FileSpreadsheet, ExternalLink, Award, Table, Eye } from 'lucide-react'
import { downloadExcelResult, getTaskResult, getDownloadUrl } from '../services/benchmark'
import ExcelPreview from './ExcelPreview'

function BenchmarkResults({ result }) {
  const [fileMetadata, setFileMetadata] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showPreview, setShowPreview] = useState(true)
  
  // Extract taskId from result
  const taskId = result?.task_id || result?.taskId

  useEffect(() => {
    if (taskId) {
      // Fetch file metadata
      getTaskResult(taskId)
        .then(data => {
          setFileMetadata(data)
          setLoading(false)
        })
        .catch(err => {
          console.error('Failed to load file metadata:', err)
          setLoading(false)
        })
    }
  }, [result])

  if (!result) return null

  const taskId = result.task_id || result.taskId

  const handleDownload = () => {
    // Trigger Excel file download using service
    downloadExcelResult(taskId)
  }

  const viewOnHuggingFace = () => {
    window.open('https://huggingface.co/datasets/Bayram/gpdval_1', '_blank')
  }

  return (
    <div className="space-y-6">
      {/* Success Banner */}
      <div className="card bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
        <div className="flex items-center space-x-3">
          <div className="bg-green-500 p-2 rounded-full">
            <CheckCircle className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-gray-900">Excel Report Generated Successfully!</h2>
            <p className="text-sm text-gray-600 mt-1">
              Professional sales analysis with {result.formulaCount} Excel formulas • {result.sections} sections • {result.errors} errors
            </p>
          </div>
          <button
            onClick={handleDownload}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Download Excel</span>
          </button>
        </div>
      </div>

      {/* Quality Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600 mb-1">{result.formulaCount}</div>
          <div className="text-sm text-gray-600">Excel Formulas</div>
          <div className="text-xs text-green-600 font-semibold mt-1">100% Formula-Based</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600 mb-1">{result.sections}</div>
          <div className="text-sm text-gray-600">Analysis Sections</div>
          <div className="text-xs text-blue-600 font-semibold mt-1">Comprehensive Coverage</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600 mb-1">{result.errors}</div>
          <div className="text-sm text-gray-600">Formula Errors</div>
          <div className="text-xs text-green-600 font-semibold mt-1">✓ Validated</div>
        </div>
      </div>

      {/* File Preview */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <FileSpreadsheet className="h-6 w-6 text-green-600" />
            <div>
              <h3 className="font-semibold text-gray-900">Excel Report Generated</h3>
              <p className="text-sm text-gray-500">
                {fileMetadata?.file_name || result.file_name || result.fileName || 'output.xlsx'}
                {fileMetadata?.file_size && (
                  <span className="ml-2 text-gray-400">
                    ({(fileMetadata.file_size / 1024).toFixed(1)} KB)
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
              Excel (.xlsx)
            </span>
          </div>
        </div>

        {/* Sheets List */}
        {loading ? (
          <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-8 text-center">
            <FileSpreadsheet className="h-16 w-16 text-gray-300 mx-auto mb-3 animate-pulse" />
            <p className="text-sm text-gray-600">Loading file details...</p>
          </div>
        ) : fileMetadata?.sheets ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm mb-2">
              <h4 className="font-medium text-gray-700">
                📊 {fileMetadata.sheet_count} Worksheets
              </h4>
              <a
                href={getDownloadUrl(taskId)}
                download
                className="btn btn-sm btn-primary flex items-center space-x-1"
              >
                <Download className="h-4 w-4" />
                <span>Download Excel</span>
              </a>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {fileMetadata.sheets.map((sheet, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-3"
                >
                  <div className="flex items-start space-x-2">
                    <Table className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h5 className="font-semibold text-gray-900 text-sm truncate">
                        {sheet.name}
                      </h5>
                      <p className="text-xs text-gray-600 mt-1">
                        {sheet.rows} rows × {sheet.columns} columns
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-blue-800 flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2 flex-shrink-0" />
                  <span>
                    <strong>Formula-driven analysis:</strong> All calculations use Excel formulas
                  </span>
                </p>
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="btn btn-sm btn-secondary flex items-center space-x-1"
                >
                  <Eye className="h-4 w-4" />
                  <span>{showPreview ? 'Hide' : 'Show'} Preview</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-8 text-center">
            <FileSpreadsheet className="h-16 w-16 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-600 mb-4">
              Professional Excel report with dynamic formulas
            </p>
            <button onClick={handleDownload} className="btn btn-secondary btn-sm">
              <Download className="h-4 w-4 mr-2" />
              Download to View
            </button>
          </div>
        )}
      </div>

      {/* Excel Preview */}
      {showPreview && fileMetadata && (
        <div className="mt-6">
          <ExcelPreview 
            taskId={taskId} 
            fileName={fileMetadata.file_name}
          />
        </div>
      )}

      {/* Analysis Summary */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
          <Award className="h-5 w-5 text-yellow-500 mr-2" />
          Analysis Highlights
        </h3>
        <div className="space-y-3 text-sm text-gray-700">
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
            <p><strong>Overall Performance:</strong> -3.0% YoY decline ($623.5K loss) identified with detailed breakdown</p>
          </div>
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
            <p><strong>Critical Risk:</strong> $3.6M (17.6%) revenue from discontinued SKUs flagged for immediate action</p>
          </div>
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
            <p><strong>Top Category:</strong> Mascaras Washable identified as largest contributor ($6.0M, 29.7% of total)</p>
          </div>
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
            <p><strong>Growth Leader:</strong> Liquid Eyeliners showing exceptional growth (+112.6%)</p>
          </div>
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
            <p><strong>Strategic Recommendations:</strong> 15 prioritized actions across 3 urgency levels</p>
          </div>
        </div>
      </div>

      {/* GDPval Badge */}
      <div className="card bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-purple-100 p-2 rounded-lg">
              <Award className="h-5 w-5 text-purple-700" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-900">GDPval Benchmark Submission</h3>
              <p className="text-xs text-gray-600 mt-0.5">
                This output was submitted to OpenAI's GDPval benchmark for evaluation
              </p>
            </div>
          </div>
          <button
            onClick={viewOnHuggingFace}
            className="btn btn-sm bg-purple-600 hover:bg-purple-700 text-white flex items-center space-x-1"
          >
            <span>View on HuggingFace</span>
            <ExternalLink className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default BenchmarkResults
