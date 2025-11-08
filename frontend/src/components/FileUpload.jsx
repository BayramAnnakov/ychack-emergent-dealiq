import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { uploadFile } from '../services/api'

function FileUpload({ onUploadSuccess }) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['.csv', '.xlsx', '.xls', '.json']
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()

    if (!allowedTypes.includes(fileExt)) {
      toast.error(`File type ${fileExt} not supported. Please upload CSV, Excel, or JSON files.`)
      return
    }

    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 50MB.')
      return
    }

    setIsUploading(true)

    try {
      const result = await uploadFile(file)
      setUploadedFile(result)
      onUploadSuccess(result)
      toast.success(`Successfully uploaded ${file.name}`)
    } catch (error) {
      toast.error(error.message || 'Failed to upload file')
    } finally {
      setIsUploading(false)
    }
  }, [onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json']
    },
    maxFiles: 1,
    disabled: isUploading
  })

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Upload CRM Data</h2>

      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'}
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        {isUploading ? (
          <div className="space-y-3">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="text-sm text-gray-600">Processing your file...</p>
          </div>
        ) : uploadedFile ? (
          <div className="space-y-3">
            <CheckCircle className="h-12 w-12 text-success-500 mx-auto" />
            <div>
              <p className="text-sm font-medium text-gray-900">{uploadedFile.filename}</p>
              <p className="text-xs text-gray-500 mt-1">
                {uploadedFile.rows} rows • {uploadedFile.columns?.length} columns
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation()
                setUploadedFile(null)
              }}
              className="text-xs text-primary-600 hover:text-primary-700"
            >
              Upload a different file
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <Upload className="h-12 w-12 text-gray-400 mx-auto" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                {isDragActive ? 'Drop your file here' : 'Drag & drop your CRM export'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                or click to browse • CSV, Excel, or JSON • Max 50MB
              </p>
            </div>
          </div>
        )}
      </div>

      {uploadedFile && uploadedFile.stats && (
        <div className="mt-4 space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Quick Stats</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-gray-50 rounded p-2">
              <span className="text-gray-500">Total Rows:</span>
              <span className="ml-2 font-medium">{uploadedFile.stats.total_rows}</span>
            </div>
            <div className="bg-gray-50 rounded p-2">
              <span className="text-gray-500">Columns:</span>
              <span className="ml-2 font-medium">{uploadedFile.stats.total_columns}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload