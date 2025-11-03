# Use full Python 3.12 image (not slim)
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your app
CMD ["python", "main.py"]
