#!/bin/bash

# Simple entrypoint for Google Meet Bot API
echo "Starting Google Meet Bot API..."

# Load environment variables from .env file if it exists
if [ -f "/app/.env" ]; then
    echo "Loading environment variables from .env file"
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

# Start the API
exec python api.py