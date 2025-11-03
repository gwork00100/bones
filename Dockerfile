# Use Python slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for distutils and some Python packages
RUN apt-get update && \
    apt-get install -y python3-distutils gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Command to run Bones
CMD ["python", "main.py"]
