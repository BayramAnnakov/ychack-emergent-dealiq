import React, { useState, useEffect } from 'react'
import * as XLSX from 'xlsx'
import { FileSpreadsheet, Download, ExternalLink, Loader, AlertCircle } from 'lucide-react'

/**
 * Component to preview reference Excel/CSV files from URLs
 * Similar to ExcelPreview but loads from external URLs
 */
function ReferenceFilePreview({ fileUrl, fileName }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [workbookData, setWorkbookData] = useState(null)
  const [activeSheet, setActiveSheet] = useState(0)

  useEffect(() => {
    if (fileUrl) {
      loadFileFromUrl()
    }
  }, [fileUrl])

  const loadFileFromUrl = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch the file from URL
      const response = await fetch(fileUrl)
      if (!response.ok) {
        throw new Error(`Failed to fetch file: ${response.statusText}`)
      }

      const arrayBuffer = await response.arrayBuffer()
      const workbook = XLSX.read(arrayBuffer, { type: 'array' })

      // Convert workbook to usable data
      const sheets = workbook.SheetNames.map(name => {
        const worksheet = workbook.Sheets[name]
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })
        return {
          name,
          data: jsonData
        }
      })

      setWorkbookData(sheets)
      setLoading(false)
    } catch (err) {
      console.error('Error loading reference file:', err)
      setError(err.message || 'Failed to load file')
      setLoading(false)
    }
  }

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = fileUrl
    link.download = fileName || 'reference_file.xlsx'
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const getGoogleSheetsImportUrl = () => {
    // Use the proxy URL which should be accessible by Google Sheets
    // Google Sheets import URL format
    const baseUrl = window.location.origin
    const fullProxyUrl = fileUrl.startsWith('http') ? fileUrl : `${baseUrl}${fileUrl}`
    return `https://docs.google.com/spreadsheets/d/new/import?url=${encodeURIComponent(fullProxyUrl)}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="h-6 w-6 text-blue-600 animate-spin mr-2" />
        <span className="text-gray-600">Loading reference file...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
          <div>
            <h4 className="font-medium text-red-900">Failed to load reference file</h4>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={handleDownload}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Try downloading instead
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!workbookData || workbookData.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FileSpreadsheet className="h-12 w-12 mx-auto mb-2 text-gray-400" />
        <p>No data available</p>
      </div>
    )
  }

  const currentSheet = workbookData[activeSheet]

  return (
    <div className="space-y-4">
      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileSpreadsheet className="h-5 w-5 text-blue-600" />
          <span className="font-medium text-gray-900">{fileName || 'Reference File'}</span>
        </div>
        <button
          onClick={handleDownload}
          className="btn btn-sm btn-primary flex items-center space-x-1"
        >
          <Download className="h-4 w-4" />
          <span>Download</span>
        </button>
      </div>

      {/* Sheet tabs */}
      {workbookData.length > 1 && (
        <div className="flex space-x-2 border-b border-gray-200">
          {workbookData.map((sheet, index) => (
            <button
              key={index}
              onClick={() => setActiveSheet(index)}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                activeSheet === index
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {sheet.name}
            </button>
          ))}
        </div>
      )}

      {/* Table preview */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <tbody className="bg-white divide-y divide-gray-200">
              {currentSheet.data.slice(0, 50).map((row, rowIndex) => (
                <tr key={rowIndex} className={rowIndex === 0 ? 'bg-gray-50' : ''}>
                  {row.map((cell, cellIndex) => (
                    <td
                      key={cellIndex}
                      className={`px-3 py-2 text-sm whitespace-nowrap border-r border-gray-200 last:border-r-0 ${
                        rowIndex === 0 ? 'font-semibold text-gray-900' : 'text-gray-700'
                      }`}
                    >
                      {cell !== null && cell !== undefined && cell !== '' 
                        ? String(cell) 
                        : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {currentSheet.data.length > 50 && (
          <div className="bg-gray-50 px-4 py-2 text-sm text-gray-600 border-t border-gray-200">
            Showing first 50 rows of {currentSheet.data.length} total rows
          </div>
        )}
      </div>
    </div>
  )
}

export default ReferenceFilePreview
