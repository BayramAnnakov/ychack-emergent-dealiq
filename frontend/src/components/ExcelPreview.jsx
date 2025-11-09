import React, { useState, useEffect } from 'react'
import { FileSpreadsheet, Download, ExternalLink, ChevronDown, ChevronRight } from 'lucide-react'
import * as XLSX from 'xlsx'
import { downloadExcelResult } from '../services/benchmark'

function ExcelPreview({ taskId, fileName }) {
  const [workbook, setWorkbook] = useState(null)
  const [selectedSheet, setSelectedSheet] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expandedSheets, setExpandedSheets] = useState({})

  useEffect(() => {
    console.log('ExcelPreview mounted for taskId:', taskId)
    if (taskId) {
      loadExcelFile()
    } else {
      console.error('No taskId provided to ExcelPreview')
      setError('No task ID provided')
      setLoading(false)
    }
  }, [taskId])

  const loadExcelFile = async () => {
    try {
      setLoading(true)
      console.log('Loading Excel file for task:', taskId)
      
      const response = await fetch(`/api/v1/benchmark/file/${taskId}`)
      console.log('Response status:', response.status, response.statusText)
      
      if (!response.ok) {
        throw new Error(`Failed to load Excel file: ${response.status} ${response.statusText}`)
      }

      const arrayBuffer = await response.arrayBuffer()
      console.log('Received arrayBuffer, size:', arrayBuffer.byteLength)
      
      const wb = XLSX.read(arrayBuffer, { type: 'array' })
      console.log('Workbook loaded with sheets:', wb.SheetNames)
      
      setWorkbook(wb)
      setLoading(false)
    } catch (err) {
      console.error('Error loading Excel:', err)
      setError(err.message)
      setLoading(false)
    }
  }

  const toggleSheet = (index) => {
    setExpandedSheets(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const openInGoogleSheets = () => {
    // First download the file
    const downloadUrl = `/api/v1/benchmark/download/${taskId}`
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${taskId}_output.xlsx`
    link.click()
    
    // Then open Google Sheets with import instructions
    setTimeout(() => {
      window.open('https://docs.google.com/spreadsheets/u/0/create', '_blank')
      alert('File is downloading! After it completes:\n\n1. In the new Google Sheets tab, click File → Import\n2. Click Upload tab\n3. Drag the downloaded file or click Select a file\n4. Click Import data')
    }, 500)
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <FileSpreadsheet className="h-12 w-12 text-gray-400 mx-auto mb-3 animate-pulse" />
        <p className="text-gray-600">Loading Excel preview for {taskId}...</p>
        <p className="text-xs text-gray-500 mt-2">Check browser console for details</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-lg border border-red-200 p-6">
        <p className="text-red-800">Failed to load Excel preview: {error}</p>
        <a
          href={`/api/v1/benchmark/download/${taskId}`}
          download
          className="btn btn-sm btn-secondary mt-3 inline-flex items-center"
        >
          <Download className="h-4 w-4 mr-2" />
          Download Excel File
        </a>
      </div>
    )
  }

  if (!workbook) return null

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileSpreadsheet className="h-6 w-6 text-green-600" />
            <div>
              <h3 className="font-semibold text-gray-900">{fileName || 'Excel Preview'}</h3>
              <p className="text-sm text-gray-500">{workbook.SheetNames.length} worksheets</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={openInGoogleSheets}
              className="btn btn-sm btn-secondary flex items-center space-x-1"
            >
              <ExternalLink className="h-4 w-4" />
              <span>Open in Sheets</span>
            </button>
            <a
              href={`/api/v1/benchmark/download/${taskId}`}
              download
              className="btn btn-sm btn-primary flex items-center space-x-1"
            >
              <Download className="h-4 w-4" />
              <span>Download</span>
            </a>
          </div>
        </div>
      </div>

      {/* Sheet Tabs and Content */}
      <div className="p-4 space-y-4">
        {workbook.SheetNames.map((sheetName, index) => {
          const sheet = workbook.Sheets[sheetName]
          const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' })
          const isExpanded = expandedSheets[index]

          return (
            <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Sheet Header */}
              <button
                onClick={() => toggleSheet(index)}
                className="w-full flex items-center justify-between p-3 bg-blue-50 hover:bg-blue-100 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  {isExpanded ? (
                    <ChevronDown className="h-5 w-5 text-blue-600" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-blue-600" />
                  )}
                  <FileSpreadsheet className="h-5 w-5 text-blue-600" />
                  <span className="font-medium text-gray-900">{sheetName}</span>
                  <span className="text-sm text-gray-500">
                    ({jsonData.length} rows × {jsonData[0]?.length || 0} cols)
                  </span>
                </div>
              </button>

              {/* Sheet Content */}
              {isExpanded && (
                <div className="overflow-auto max-h-96 bg-white">
                  <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <tbody className="divide-y divide-gray-200">
                      {jsonData.slice(0, 50).map((row, rowIndex) => (
                        <tr key={rowIndex} className={rowIndex === 0 ? 'bg-gray-50 font-semibold' : 'hover:bg-gray-50'}>
                          {row.map((cell, cellIndex) => (
                            <td
                              key={cellIndex}
                              className="px-3 py-2 whitespace-nowrap text-gray-900 border-r border-gray-100"
                            >
                              {cell !== null && cell !== undefined ? String(cell) : ''}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {jsonData.length > 50 && (
                    <div className="p-3 bg-gray-50 text-center text-sm text-gray-600">
                      Showing first 50 rows. Download to see all {jsonData.length} rows.
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Footer Note */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <p className="text-sm text-gray-600 text-center">
          💡 <strong>Tip:</strong> All calculations use Excel formulas. Download the file to see and edit formulas.
        </p>
      </div>
    </div>
  )
}

export default ExcelPreview
