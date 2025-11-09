/**
 * Benchmark API Service
 * Handles communication with GDPval benchmark endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

/**
 * Fetch list of available benchmark tasks
 */
export async function fetchBenchmarkTasks() {
  const response = await fetch(`${API_BASE_URL}/benchmark/tasks`)
  if (!response.ok) {
    throw new Error('Failed to fetch benchmark tasks')
  }
  return await response.json()
}

/**
 * Execute a benchmark task with streaming progress updates
 * @param {string} taskId - The task ID to execute
 * @param {object} callbacks - Callbacks for progress updates
 * @param {function} callbacks.onProgress - Called with (message, progress) during execution
 * @param {function} callbacks.onComplete - Called when task completes successfully
 * @param {function} callbacks.onError - Called if task fails
 */
export async function executeBenchmarkTask(taskId, callbacks = {}) {
  const { onProgress, onComplete, onError } = callbacks

  try {
    const response = await fetch(`${API_BASE_URL}/benchmark/execute/${taskId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('Failed to start benchmark task')
    }

    // Handle streaming response
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      // Decode the chunk
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.status === 'complete') {
              // Task completed
              if (onComplete) {
                onComplete({
                  taskId: data.task_id,
                  fileName: data.file_name,
                  formulaCount: data.formula_count,
                  sections: data.sections,
                  errors: data.errors
                })
              }
            } else {
              // Progress update
              if (onProgress) {
                onProgress(data.status, data.progress)
              }
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e)
          }
        }
      }
    }
  } catch (error) {
    console.error('Benchmark execution error:', error)
    if (onError) {
      onError(error)
    }
    throw error
  }
}

/**
 * Get task history (completed tasks)
 * @returns {Promise<object>} List of completed tasks
 */
export async function getTaskHistory() {
  const response = await fetch(`${API_BASE_URL}/benchmark/history`)
  if (!response.ok) {
    throw new Error('Failed to fetch task history')
  }
  return await response.json()
}

/**
 * Get task result metadata
 * @param {string} taskId - The task ID
 * @returns {Promise<object>} Result metadata including sheets info
 */
export async function getTaskResult(taskId) {
  const response = await fetch(`${API_BASE_URL}/benchmark/result/${taskId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch task result')
  }
  return await response.json()
}

/**
 * Download the Excel result file
 * @param {string} taskId - The task ID
 * @returns {string} Download URL
 */
export function getDownloadUrl(taskId) {
  const url = `${API_BASE_URL}/benchmark/download/${taskId}`
  return url
}

/**
 * Download Excel result file
 * @param {string} taskId - The task ID
 */
export async function downloadExcelResult(taskId) {
  const url = `${API_BASE_URL}/benchmark/download/${taskId}`
  
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error('Failed to download file')
    }
    
    // Get the blob
    const blob = await response.blob()
    
    // Create a download link
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `${taskId}_output.xlsx`
    document.body.appendChild(a)
    a.click()
    
    // Cleanup
    window.URL.revokeObjectURL(downloadUrl)
    document.body.removeChild(a)
  } catch (error) {
    console.error('Download failed:', error)
    // Fallback to window.open
    window.open(url, '_blank')
  }
}

/**
 * Get validation report for a task
 * @param {string} taskId - The task ID
 */
export async function getValidationReport(taskId) {
  const response = await fetch(`${API_BASE_URL}/benchmark/validate/${taskId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch validation report')
  }
  return await response.json()
}
