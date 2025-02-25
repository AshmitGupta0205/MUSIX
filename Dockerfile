FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev libasound2-dev libffi-dev ffmpeg

# Set the working directory
WORKDIR /Home

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Streamlit default port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "Home.py"]