# Use the official Python image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LD_LIBRARY_PATH="/usr/lib:/usr/local/lib"

# Install dependencies
RUN apt-get update && apt-get install -y portaudio19-dev && \
    pip install --upgrade pip setuptools wheel && \
    pip install sounddevice && \
    pip install -r requirements.txt

# Set the working directory
WORKDIR /Home

# Copy the project files
COPY . /Home

# Expose port 8501 (default for Streamlit)
EXPOSE 8501

# Command to run the Streamlit app
CMD streamlit run pages/Karaoke-Maker.py --server.port $PORT