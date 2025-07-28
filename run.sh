#!/bin/bash

echo "🤖 Starting Chatbot..."

# Check if virtual environment exists
if [ ! -d "chatbot" ]; then
    echo "❌ Virtual environment 'chatbot' not found!"
    echo "Please run setup.sh first:"
    echo "bash setup.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source chatbot/bin/activate

# Check if AWS credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️  AWS credentials not set!"
    echo "Please set your AWS credentials:"
    echo "export AWS_ACCESS_KEY_ID=your_access_key"
    echo "export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "export AWS_REGION=us-east-1"
    echo ""
    echo "Or create a .env file in the backend directory"
fi

# Start the backend
echo "🚀 Starting FastAPI backend..."
cd backend
python main.py 