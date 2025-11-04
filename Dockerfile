# Use full Python 3.12 image (includes distutils)
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy only the requirements first (caching benefit)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the port your app will run on (Render default is $PORT)
ENV PORT=10000
EXPOSE $PORT

# Set environment variables for Redis and other secrets if needed
# ENV UPSTASH_URL=<your-url>
# ENV UPSTASH_TOKEN=<your-token>

# Run the main app
CMD ["python", "main.py"]
