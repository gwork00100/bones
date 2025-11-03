# Use Python slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && \
    apt-get install -y gcc libffi-dev python3.12-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run Bones
CMD ["python", "main.py"]
