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

export default api