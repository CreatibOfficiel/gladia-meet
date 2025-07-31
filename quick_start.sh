#!/bin/bash

echo "🚀 Google Meet Bot - Quick Start"
echo "================================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Setting up environment configuration..."
    python3 setup_env.py --create
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create .env file"
        exit 1
    fi
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your actual values:"
    echo "   nano .env"
    echo ""
    echo "After editing .env, run this script again."
    exit 0
fi

# Validate .env
echo "🔍 Validating configuration..."
python3 setup_env.py --validate
if [ $? -ne 0 ]; then
    echo "❌ Configuration validation failed"
    echo "Please edit .env file and try again"
    exit 1
fi

# Build Docker image if not exists
echo "🐳 Building Docker image..."
if [[ "$(docker images -q gmeet 2> /dev/null)" == "" ]]; then
    ./build.sh
    if [ $? -ne 0 ]; then
        echo "❌ Docker build failed"
        exit 1
    fi
else
    echo "✅ Docker image already exists"
fi

# Start API
echo "🚀 Starting API server..."
docker-compose up -d gmeet-api
if [ $? -ne 0 ]; then
    echo "❌ Failed to start API server"
    exit 1
fi

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
sleep 5

# Test API
echo "🧪 Testing API..."
python3 test_api.py --quick-test
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   - API is running at: http://localhost:8000"
    echo "   - API docs: http://localhost:8000/docs"
    echo "   - Test the API: python3 test_api.py"
    echo "   - View logs: docker-compose logs -f gmeet-api"
    echo ""
else
    echo "⚠️  API test failed, but server might still be starting"
    echo "   Check logs: docker-compose logs gmeet-api"
fi 