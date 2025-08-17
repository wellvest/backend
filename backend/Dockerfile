# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory for backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    ca-certificates \
    libxrender1 \
    libx11-dev \
    libfontconfig1 \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6/wkhtmltox_0.12.6-1.bionic_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6-1.bionic_amd64.deb \
    && apt-get install -f -y \
    && rm wkhtmltox_0.12.6-1.bionic_amd64.deb

# Copy backend requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port 8000 for the application
EXPOSE 8000

# Command to run the backend application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
