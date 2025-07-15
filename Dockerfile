# Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy everything into the container
COPY . .

# Install dependencies
RUN pip install .

# Use CLI entry point
ENTRYPOINT ["kahoot-to-anki"]
