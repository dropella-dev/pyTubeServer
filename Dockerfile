# Use official Python image as base
FROM python:3.11-slim

# Install Node.js (LTS)
RUN apt-get update && apt-get install -y curl gnupg \
 && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y nodejs \
 && apt-get clean

# Create working directory
WORKDIR /app

# Copy your project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Railway will listen on
EXPOSE 5000

# Start the Flask server
CMD ["python", "app.py"]
