FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads

# Expose ports
EXPOSE 8000 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
