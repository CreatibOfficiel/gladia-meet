#!/bin/bash

# Google Meet Bot API - Build Script
set -e

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from env.example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "Created .env file. Please edit it with your values."
    else
        echo "Error: env.example file not found."
        exit 1
    fi
fi

# Create necessary directories
mkdir -p recordings screenshots logs
chmod 755 recordings screenshots logs

# Build the Docker image
echo "Building Docker image..."

# Check if running on Apple Silicon
BUILD_ARGS=""
if [[ $(uname -m) == "arm64" ]]; then
    echo "Detected Apple Silicon (ARM64)"
    BUILD_ARGS="--platform linux/arm64"
fi

# Build the image
docker build $BUILD_ARGS \
    --tag gmeet-bot-api:latest \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "To run: docker-compose up gmeet-api"
    echo "API will be available at: http://localhost:8000"
else
    echo "Build failed!"
    exit 1
fi