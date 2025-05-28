# Use a slim Python base image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (aria2 for downloads, build essentials for some Python packages)
RUN apt-get update && apt-get install -y \
    aria2 \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# Copy all application files
COPY . .

# Load environment variables from .env file
RUN pip install python-dotenv
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python3", "main.py"]
