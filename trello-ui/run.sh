#!/bin/bash
# Quick start script for Trello Archive UI

echo "🚀 Starting Trello Archive UI..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if database exists
if [ ! -f "../trello_archive.db" ]; then
    echo "⚠️  Warning: trello_archive.db not found in parent directory"
    echo "   Expected location: ../trello_archive.db"
    echo ""
fi

# Run the application
echo "🌐 Starting Dash server..."
echo "📊 Dashboard: http://127.0.0.1:8050"
echo "🔍 Search: http://127.0.0.1:8050/search"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
