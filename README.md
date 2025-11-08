# DealIQ - Every Rep's Personal Data Scientist

DealIQ transforms sales teams by providing AI-powered CRM intelligence that surfaces hidden insights, predicts deal outcomes, and validates sales hypotheses in seconds.

## Features

- **Instant Insight Extraction**: Upload any CRM export and get actionable insights in 60 seconds
- **Predictive Deal Intelligence**: AI identifies at-risk opportunities and predicts outcomes
- **Hypothesis Testing**: Validate sales strategies with data-backed analysis in seconds
- **Multi-Agent System**: Specialized AI agents working together to analyze your sales data

## Tech Stack

- **Backend**: FastAPI + Claude Agent SDK
- **Frontend**: React + Tailwind CSS
- **Data Processing**: pandas, numpy, scikit-learn
- **Database**: PostgreSQL + Redis
- **Infrastructure**: Docker

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Using Docker

```bash
docker-compose up
```

## Project Structure

```
dealiq/
├── backend/           # FastAPI backend with Claude Agent SDK
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── agents/   # AI agents for different tasks
│   │   ├── core/     # Core functionality
│   │   ├── models/   # Data models
│   │   └── services/ # Business logic
│   └── .claude/      # Claude agent configurations
├── frontend/         # React frontend
│   └── src/
│       ├── components/ # Reusable UI components
│       ├── pages/     # Page components
│       └── services/  # API services
└── data/            # Sample data and uploads
```

## API Documentation

Once the backend is running, visit:
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Development

This project was built during a 30+ hour hackathon to demonstrate the power of multi-agent systems for sales intelligence.

## License

MIT