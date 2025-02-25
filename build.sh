#!/bin/bash

# Ensure the correct Python version is used
if [ -f "runtime.txt" ]; then
    PYTHON_VERSION=$(cat runtime.txt | tr -d 'python-')
    echo "Using Python version: $PYTHON_VERSION"
else
    PYTHON_VERSION="3.10"  # Default to 3.10 if runtime.txt is missing
    echo "runtime.txt not found! Using default Python $PYTHON_VERSION"
fi

# Install system dependencies
sudo apt-get update && sudo apt-get install -y \
    portaudio19-dev libasound2-dev libffi-dev ffmpeg python3-dev gcc g++ make pkg-config autoconf automake wget

# Set environment variables for PortAudio
export CFLAGS="-I/usr/local/include"
export LDFLAGS="-L/usr/local/lib"
export LD_LIBRARY_PATH="/usr/local/lib"

# Ensure pip, setuptools, and wheel are up to date
python -m pip install --upgrade pip setuptools wheel

# Install PyAudio only if needed
if grep -q "PyAudio" requirements.txt; then
    pip install --no-cache-dir --global-option="build_ext" --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib" pyaudio
fi

# Install all dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ ERROR: requirements.txt not found!"
    exit 1  # Stop the build if missing
fi

# Verify Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️ Streamlit not found! Installing manually..."
    pip install streamlit
fi

echo "✅ Build script executed successfully!"