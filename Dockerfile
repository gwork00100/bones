# Use Python slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run Bones
CMD ["python", "main.py"]
