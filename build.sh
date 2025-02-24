#!/bin/bash

# Update package list and install dependencies
apt-get update && apt-get install -y portaudio19-dev ffmpeg

# Ensure pip is up to date
pip install --upgrade pip

# Check if requirements.txt exists before installing
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ ERROR: requirements.txt not found!"
    exit 1  # Stop the build if missing
fi

# Print success message
echo "✅ Build script executed successfully!"