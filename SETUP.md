# DealIQ Setup & Testing Guide

## Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend development)
- Docker and Docker Compose (optional)
- Anthropic API Key (for Claude integration)

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ychack-emergent-dealiq

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY=your_api_key_here

# 3. Start all services
docker-compose up

# Access the application:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## Manual Setup

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Create necessary directories
mkdir -p data/uploads

# Run the backend
uvicorn app.main:app --reload

# Or use the startup script
./start.sh
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:5173
```

## Testing the Application

### 1. Upload Sample Data

1. Open the frontend at http://localhost:5173
2. Use the drag-and-drop area to upload `data/sample_crm_data.csv`
3. The file will be processed and basic statistics will appear

### 2. Test Natural Language Queries

Try these example queries:

**Analysis Queries:**
- "What are my top opportunities?"
- "Show me the pipeline breakdown by stage"
- "Who are my top performers?"

**Predictive Queries:**
- "Which deals will close this quarter?"
- "What's the likelihood of hitting quota?"
- "Identify deals at risk of churning"

**Hypothesis Testing:**
- "Do longer sales cycles mean bigger deals?"
- "Are multi-threaded deals more successful?"
- "Does deal stage correlate with win rate?"

### 3. API Testing

You can also test the API directly:

```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Upload a file
curl -X POST http://localhost:8000/api/v1/upload/csv \
  -F "file=@data/sample_crm_data.csv"

# Get quick insights (replace FILE_ID with actual ID from upload response)
curl http://localhost:8000/api/v1/insights/quick/FILE_ID

# Test a hypothesis
curl -X POST http://localhost:8000/api/v1/insights/hypothesis \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "FILE_ID",
    "hypothesis": "Larger deals take longer to close"
  }'
```

### 4. WebSocket Testing

The application supports real-time agent communication via WebSocket:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/agents/chat');

ws.onopen = () => {
  // Send a query
  ws.send(JSON.stringify({
    type: 'query',
    query: 'Analyze my pipeline health',
    file_id: 'YOUR_FILE_ID'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Architecture Overview

### Multi-Agent System

The application uses a multi-agent architecture with specialized agents:

1. **DataIngestionAgent**: Handles data parsing and normalization
2. **AnalyticsAgent**: Performs statistical analysis
3. **PredictiveAgent**: ML-based predictions
4. **InsightAgent**: Natural language insights
5. **HypothesisAgent**: Tests business hypotheses
6. **OrchestratorAgent**: Coordinates all agents

### Technology Stack

- **Backend**: FastAPI + Claude Agents SDK
- **Frontend**: React + Tailwind CSS
- **Data Processing**: pandas, numpy, scikit-learn
- **AI**: Claude 3.5 Sonnet via Anthropic API

## Configuration

### Environment Variables

Key environment variables in `backend/.env`:

```env
# Required
ANTHROPIC_API_KEY=your_key_here

# Optional
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_UPLOAD_SIZE=52428800
```

### Claude Agent Configuration

The agents are configured to use Claude SDK with streaming support. Each agent has specific tools and permissions defined in `backend/app/agents/base.py`.

## Troubleshooting

### Common Issues

1. **"Module claude_agent_sdk not found"**
   ```bash
   pip install claude-agent-sdk
   ```

2. **"Cannot connect to backend"**
   - Ensure backend is running on port 8000
   - Check CORS settings in `backend/app/main.py`

3. **"File upload fails"**
   - Check file size (max 50MB by default)
   - Ensure `data/uploads` directory exists
   - Verify file format (CSV, Excel, JSON)

4. **"No insights generated"**
   - Verify ANTHROPIC_API_KEY is set
   - Check agent logs in console
   - Ensure data has sufficient rows

### Debug Mode

Enable debug logging:

```python
# In backend/app/core/config.py
DEBUG = True
```

View agent execution:
```bash
# Watch backend logs
uvicorn app.main:app --reload --log-level debug
```

## Performance Optimization

- For large files (>10MB), consider chunking
- Use Redis for caching agent results
- Enable parallel agent execution in orchestrator
- Implement session management for repeated queries

## Security Considerations

- Never commit `.env` files
- Use environment variables for sensitive data
- Implement authentication before production
- Sanitize file uploads
- Rate limit API endpoints

## Next Steps

1. Add authentication and user management
2. Implement real CRM integrations (Salesforce, HubSpot)
3. Add more sophisticated ML models
4. Create custom agent configurations
5. Build export functionality
6. Add team collaboration features

## Support

For issues or questions about the hackathon project, please refer to the vision document or create an issue in the repository.