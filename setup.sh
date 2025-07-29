#!/bin/bash

echo "🔧 Setting up AWS Chatbot with RAG..."

# Create virtual environment with Python 3.11
echo "📦 Creating virtual environment with Python 3.11..."
python3.11 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r backend/requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Configure AWS credentials: cp backend/env.example backend/.env"
echo "2. Start the application: bash run.sh"
echo "3. Open frontend: cd frontend && python -m http.server 8080" 