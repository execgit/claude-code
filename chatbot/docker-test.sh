#!/bin/bash

# Docker test script for LLM chatbot

set -e

echo "🐳 LLM Chatbot Docker Test Script"
echo "=================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your LLM API key and configuration"
    echo "   Required: LLM_API_KEY"
    echo "   Optional: LLM_API_BASE_URL (for custom endpoints)"
    exit 1
fi

# Source environment variables
source .env

# Check if API key is set
if [ -z "$LLM_API_KEY" ]; then
    echo "❌ LLM_API_KEY not set in .env file"
    exit 1
fi

echo "✅ Environment configured"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t llm-chatbot .

# Initialize knowledge base
echo "📚 Initializing knowledge base..."
docker-compose --profile init up chatbot-init

# Start the chatbot
echo "🚀 Starting chatbot..."
echo "   Type 'quit' or 'exit' to stop"
echo "   Press Ctrl+C to exit Docker container"
echo ""

docker-compose up chatbot