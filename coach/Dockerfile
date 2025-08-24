# Use a suitable Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama CLI
RUN curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service in the background, pull the model, and stop the service
RUN ollama serve & \
    sleep 30 && \
    ollama pull llama3.2

# Copy your application code to the container
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by Ollama (assume it's 11434)
EXPOSE 11434

# Start the Ollama service at container startup
ENTRYPOINT ["ollama", "serve"]