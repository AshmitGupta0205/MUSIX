#!/bin/bash

# Update and install necessary dependencies
sudo apt-get update && sudo apt-get install -y \
    libasound2-dev libffi-dev ffmpeg python3-dev gcc g++ make pkg-config autoconf automake wget

# Ensure pip is up to date
pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ ERROR: requirements.txt not found!"
    exit 1  # Stop the build if missing
fi

echo "✅ Build script executed successfully!"