#!/bin/bash

# Update package list and install required dependencies
apt-get update && apt-get install -y \
    portaudio19-dev \
    libasound2-dev \
    libffi-dev \
    ffmpeg \
    python3-dev \
    gcc \
    g++ \
    make \
    pkg-config

# Manually install PortAudio (Fix missing headers)
cd /tmp
wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz
tar -xvzf pa_stable_v190700_20210406.tgz
cd portaudio
./configure && make && make install
cd ..

# Ensure pip and virtual environment are up to date
pip install --upgrade pip setuptools wheel

# Check if requirements.txt exists before installing
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ ERROR: requirements.txt not found!"
    exit 1  # Stop the build if missing
fi

# Print success message
echo "✅ Build script executed successfully!"
