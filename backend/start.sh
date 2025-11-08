#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/uploads

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it and add your ANTHROPIC_API_KEY"
        echo "   Edit .env and set: ANTHROPIC_API_KEY=your_key_here"
        echo ""
    else
        echo "❌ No .env.example file found. Please create a .env file with:"
        echo "   ANTHROPIC_API_KEY=your_key_here"
        exit 1
    fi
fi

# Check if ANTHROPIC_API_KEY is set in .env
if ! grep -q "ANTHROPIC_API_KEY=.*[^=]" .env; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY appears to be empty in .env file"
    echo "   Please edit .env and set your API key"
fi

# Load environment variables from .env file
export $(cat .env | grep -v '^#' | xargs)

# Run the application
echo "Starting DealIQ backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000