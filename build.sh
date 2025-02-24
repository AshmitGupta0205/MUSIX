#!/bin/bash

# Update and install required dependencies
apt-get update && apt-get install -y \
    portaudio19-dev libasound2-dev libffi-dev ffmpeg python3-dev gcc g++ make pkg-config

# Ensure pip is up to date
pip install --upgrade pip setuptools wheel

# Find requirements.txt dynamically
REQ_FILE=$(find /opt/render/project/src -name "requirements.txt" | head -n 1)

if [ -z "$REQ_FILE" ]; then
    echo "❌ ERROR: requirements.txt not found!"
    exit 1
else
    echo "📄 Found requirements.txt at $REQ_FILE"
    pip install -r "$REQ_FILE"
fi

# Print success message
echo "✅ Build script executed successfully!"