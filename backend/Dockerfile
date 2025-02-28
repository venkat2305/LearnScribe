# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Create a working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    # Example: ffmpeg for audio processing
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]