#!/bin/bash

# Navigate to the client directory
cd ../client

# Build the frontend
echo "Building frontend..."
npm run build

# Navigate back to backend
cd ../backend

# Create frontend directory if it doesn't exist
mkdir -p frontend

# Copy the built frontend files to the backend/frontend directory
echo "Copying frontend build to backend/frontend..."
cp -r ../client/dist/* ./frontend/

# Build the Docker image
echo "Building Docker image..."
sudo docker build -t wellvest-app .

echo "Docker build complete. Run with: sudo docker run -p 8000:8000 wellvest-app"
