import React, { useState } from 'react'
import { FileText, Download, ExternalLink, AlertCircle } from 'lucide-react'
import { downloadExcelResult } from '../services/benchmark'

/**
 * Component to preview PDF files
 * Uses browser's native PDF rendering
 */
function PdfPreview({ taskId, fileName }) {
  const [error, setError] = useState(null)
  
  const pdfUrl = `/api/v1/benchmark/file/${taskId}`
  
  const handleDownload = () => {
    downloadExcelResult(taskId)
  }

  const handleError = () => {
    setError('Failed to load PDF preview')
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-lg border border-red-200 p-6">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
          <div>
            <h4 className="font-medium text-red-900">Failed to load PDF preview</h4>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={handleDownload}
              className="mt-3 btn btn-sm btn-secondary"
            >
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6 text-red-600" />
            <div>
              <h3 className="font-semibold text-gray-900">{fileName || 'PDF Preview'}</h3>
              <p className="text-sm text-gray-500">PDF Document</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownload}
              className="btn btn-sm btn-primary flex items-center space-x-1"
            >
              <Download className="h-4 w-4" />
              <span>Download</span>
            </button>
          </div>
        </div>
      </div>

      {/* PDF Viewer */}
      <div className="p-4">
        <div className="border border-gray-300 rounded-lg overflow-hidden" style={{ height: '800px' }}>
          <iframe
            src={pdfUrl}
            className="w-full h-full"
            title="PDF Preview"
            onError={handleError}
          />
        </div>
      </div>

      {/* Footer Note */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <p className="text-sm text-gray-600 text-center">
          💡 <strong>Tip:</strong> Download the PDF to view with full features and annotations.
        </p>
      </div>
    </div>
  )
}

export default PdfPreview
