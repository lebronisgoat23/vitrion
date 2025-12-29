# Base Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install System Dependencies (Required for OpenCV/MediaPipe)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Layer caching)
COPY requirements.txt .

# Install Python Dependencies
# No cache dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (Documentation only, usually overriden by runtime)
EXPOSE 8000

# Run the application
# We use shell form to allow expansion of $PORT if provided by host (e.g. Railway/Heroku)
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
