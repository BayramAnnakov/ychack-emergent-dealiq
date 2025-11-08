import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000, // 2 minutes for long-running AI operations
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

// Upload endpoints
export const uploadFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload/csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  })

  return response
}

export const getUploadStatus = async (fileId) => {
  return api.get(`/upload/status/${fileId}`)
}

export const deleteUpload = async (fileId) => {
  return api.delete(`/upload/${fileId}`)
}

// Insights endpoints
export const analyzeData = async (fileId, query, insightType = 'general') => {
  return api.post('/insights/analyze', {
    file_id: fileId,
    query,
    insight_type: insightType
  })
}

export const getQuickInsights = async (fileId) => {
  return api.get(`/insights/quick/${fileId}`)
}

export const testHypothesis = async (fileId, hypothesis) => {
  return api.post('/insights/hypothesis', {
    file_id: fileId,
    hypothesis
  })
}

export const predictOutcomes = async (fileId, predictionType, target = null) => {
  return api.post('/insights/predict', {
    file_id: fileId,
    prediction_type: predictionType,
    target
  })
}

// Agent endpoints
export const listAgents = async () => {
  return api.get('/agents/')
}

export const queryAgent = async (agentType, query, context = null) => {
  return api.post('/agents/query', {
    agent_type: agentType,
    query,
    context
  })
}

export const getAgentsStatus = async () => {
  return api.get('/agents/status')
}

// WebSocket connection for real-time chat
export const createAgentWebSocket = (onMessage, onError) => {
  const wsUrl = `ws://localhost:8000/api/v1/agents/chat`
  const ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('WebSocket connected')
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    onError(error)
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected')
  }

  return {
    send: (message) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message))
      }
    },
    close: () => ws.close()
  }
}

// Health check
export const checkHealth = async () => {
  return api.get('/health/')
}

// Streaming analysis with Server-Sent Events (SSE)
export const analyzeDataStreaming = async (fileId, query, analysisType = 'general', callbacks = {}) => {
  const {
    onStatus = () => {},
    onPartial = () => {},
    onTool = () => {},
    onComplete = () => {},
    onError = () => {}
  } = callbacks

  console.log('=== STARTING STREAMING ANALYSIS ===')
  console.log('File ID:', fileId)
  console.log('Query:', query)
  console.log('Analysis Type:', analysisType)

  return new Promise((resolve, reject) => {
    // Use fetch for SSE
    const url = `/api/v1/streaming/analyze-stream`

    console.log('Fetching URL:', url)

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_id: fileId,
        query: query,
        analysis_type: analysisType
      })
    })
      .then(response => {
        console.log('Response received, status:', response.status)

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        console.log('Starting to read stream...')

        // Read stream
        function readStream() {
          reader.read().then(({ done, value }) => {
            if (done) {
              console.log('Stream ended')
              return
            }

            // Decode chunk
            buffer += decoder.decode(value, { stream: true })

            // Process complete messages
            const lines = buffer.split('\n\n')
            buffer = lines.pop() || '' // Keep incomplete message in buffer

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6)) // Remove 'data: ' prefix
                  console.log('SSE message received:', data.type, data)

                  // Handle different message types
                  switch (data.type) {
                    case 'status':
                      console.log('Status update:', data.message, data.progress)
                      onStatus(data)
                      break
                    case 'partial':
                      console.log('Partial content received, length:', data.content?.length)
                      onPartial(data)
                      break
                    case 'tool':
                      console.log('Tool usage:', data.tool_name)
                      onTool(data)
                      break
                    case 'complete':
                      console.log('Analysis complete!')
                      onComplete(data)
                      resolve(data)
                      return
                    case 'error':
                      console.error('Error from server:', data.message)
                      onError(data)
                      reject(new Error(data.message))
                      return
                  }
                } catch (e) {
                  console.error('Error parsing SSE message:', e, line)
                }
              }
            }

            // Continue reading
            readStream()
          }).catch(error => {
            console.error('Stream read error:', error)
            onError({ message: error.message })
            reject(error)
          })
        }

        readStream()
      })
      .catch(error => {
        console.error('Fetch error:', error)
        onError({ message: error.message })
        reject(error)
      })
  })
}

export default api