#!/bin/bash

# Chayannito 26 Email Notification System Startup Script

echo "🚀 Starting Chayannito 26 Email Notification System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your ZeptoMail API key before using email functionality."
fi

# Start the email service
echo "📧 Starting Email Notification Service..."
echo "🌐 Email service will be available at: http://localhost:5000"
echo "📊 Open index.html in your browser to access the order dashboard"
echo "🔄 The dashboard will automatically detect the email service"
echo ""
echo "📋 Available endpoints:"
echo "   GET  /                 - Health check"
echo "   POST /send-order-email - Send order confirmation email"
echo "   POST /test-email       - Test email functionality"
echo "   POST /preview-email    - Preview email template"
echo ""
echo "⏹️  Press Ctrl+C to stop the service"
echo ""

# Start the Python server
python3 email_server.py