#!/bin/bash

# Update package list and install system dependencies
apt-get update && apt-get install -y portaudio19-dev libasound2-dev ffmpeg

# Ensure pip and virtual environment are up to date
pip install --upgrade pip

# Install Python dependencies from requirements.txt
pip install -r requirements.txt

# Print success message
echo "✅ Build script executed successfully!"