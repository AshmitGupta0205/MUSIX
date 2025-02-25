
pip install --upgrade pip setuptools wheel

# Install sounddevice and required dependencies
pip install sounddevice

# Set environment variables to help locate PortAudio
export LD_LIBRARY_PATH="/usr/local/lib"
export CFLAGS="-I/usr/local/include"
export LDFLAGS="-L/usr/local/lib"

echo "✅ Build script executed successfully!"