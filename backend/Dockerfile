# Single-stage build using pre-built frontend files
FROM python:3.11-slim

# Set working directory for backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Create frontend directory
RUN mkdir -p frontend

# Note: The frontend files should be copied to the container during build
# You'll need to copy the pre-built frontend files from your host machine
# This will be done in a separate step outside of this Dockerfile

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
