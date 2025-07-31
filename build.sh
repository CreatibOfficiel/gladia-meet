#!/bin/bash

echo "🔍 Detecting system architecture..."

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        PLATFORM="linux/amd64"
        echo "✅ Detected: x86_64 (AMD64)"
        ;;
    aarch64|arm64)
        PLATFORM="linux/arm64"
        echo "✅ Detected: aarch64 (ARM64)"
        ;;
    armv7l)
        PLATFORM="linux/arm/v7"
        echo "✅ Detected: armv7l (ARM32)"
        ;;
    *)
        echo "⚠️  Unknown architecture: $ARCH"
        echo "   Using default: linux/amd64"
        PLATFORM="linux/amd64"
        ;;
esac

echo "🐳 Building Docker image for platform: $PLATFORM"

# Build with detected platform
docker build --platform $PLATFORM -t gmeet -f Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "   Image: gmeet"
    echo "   Platform: $PLATFORM"
else
    echo "❌ Build failed!"
    exit 1
fi