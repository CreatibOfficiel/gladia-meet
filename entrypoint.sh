#!/bin/bash

# Start Xvfb for display
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Check if API mode is enabled
if [ "$API_MODE" = "true" ]; then
    echo "Starting API mode..."
    python3 api.py
else
    echo "Starting direct mode..."
    python3 gmeet.py
fi