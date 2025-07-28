#!/bin/bash

echo "🚀 Setting up Chatbot Environment..."

# Check if virtual environment already exists
if [ -d "chatbot" ]; then
    echo "📦 Virtual environment 'chatbot' already exists!"
    echo "🔧 Activating existing virtual environment..."
else
    # Create virtual environment
    echo "📦 Creating Python virtual environment 'chatbot'..."
    python3 -m venv chatbot
    echo "🔧 Activating virtual environment..."
fi

# Activate virtual environment
source chatbot/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo "✅ Environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate environment: source chatbot/bin/activate"
echo "2. Set AWS credentials"
echo "3. Start the backend"
echo "4. Open the frontend"
echo ""
echo "📖 See README.md for detailed instructions" 