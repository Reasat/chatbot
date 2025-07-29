#!/bin/bash

echo "🚀 Starting AWS Chatbot with RAG..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run 'bash setup.sh' first."
    exit 1
fi

# Check for AWS credentials
if [ -f "backend/.env" ]; then
    echo "📝 Loading AWS credentials from .env..."
    export $(grep -E '^(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_REGION)=' backend/.env | xargs)
    echo "✅ AWS credentials loaded"
else
    echo "⚠️  No .env file found. Create backend/.env with your AWS credentials:"
    echo "   AWS_ACCESS_KEY_ID=your_access_key"
    echo "   AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "   AWS_REGION=us-east-1"
fi

# Start the backend
echo "🔧 Starting FastAPI backend..."
cd backend
python main.py 