#!/bin/bash

echo "Webhook Redirector"
echo "=================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set default environment variables (modify as needed)
export REDIRECT_URL="http://localhost:8080/webhook"
export LISTEN_PORT=5000

echo ""
echo "Starting webhook listener..."
echo "Redirecting requests to: $REDIRECT_URL"
echo "Listening on port: $LISTEN_PORT"
echo ""

python app.py

echo ""
echo "Webhook listener stopped."