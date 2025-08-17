# Use Python 3.11 slim image as the base image
FROM python:3.11-slim

# Set working directory for backend
WORKDIR /app

# Install system dependencies (including those needed by wkhtmltopdf)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    ca-certificates \
    libxrender1 \
    libx11-dev \
    libfontconfig1 \
    libssl-dev \
    libjpeg8 \
    liblcms2-2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/* \
    # Download and install wkhtmltox (make sure to use the proper version)
    && wget -q https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6/wkhtmltox_0.12.6-1.bionic_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6-1.bionic_amd64.deb \
    # Fix broken dependencies if needed
    && apt-get install -f -y \
    # Clean up downloaded .deb file
    && rm wkhtmltox_0.12.6-1.bionic_amd64.deb

# Copy backend requirements (make sure to add the correct dependencies in requirements.txt)
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend code into the container
COPY . .

# Create uploads directory (modify according to your app's needs)
RUN mkdir -p uploads

# Expose the backend port (adjust to the one used by your app)
EXPOSE 8000

# Command to run the backend application (using Uvicorn to run a FastAPI app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
