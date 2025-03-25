# Use Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Environment variables for the container
ENV PYTHONUNBUFFERED=1 \
    PORT=5000 \
    DEPLOY_WHATSAPP_SERVER=true

# Start the application
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]