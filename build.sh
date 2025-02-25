# Install system dependencies
sudo apt-get update && sudo apt-get install -y \
    portaudio19-dev libasound2-dev libffi-dev ffmpeg python3-dev gcc g++ make pkg-config autoconf automake wget

# Set environment variables for PortAudio
export CFLAGS="-I/usr/local/include"
export LDFLAGS="-L/usr/local/lib"
export LD_LIBRARY_PATH="/usr/local/lib"

# Ensure pip is up to date
pip install --upgrade pip setuptools wheel

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ ERROR: requirements.txt not found!"
    exit 1  # Stop the build if missing
fi

echo "✅ Build script executed successfully!"