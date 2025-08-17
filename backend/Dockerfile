# Use a Python slim image for a smaller footprint.
# The `bookworm` tag indicates Debian 12, which is more recent than `bionic` (Ubuntu 18.04).
FROM python:3.11-slim-bookworm

# Set the working directory inside the container.
WORKDIR /app

# Install system dependencies.
# This single RUN command reduces the number of Docker layers.
# It installs necessary libraries for Python packages and wkhtmltopdf,
# then downloads and installs wkhtmltopdf from a stable release,
# and finally cleans up the package lists to keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxrender1 \
    libfontconfig1 \
    libjpeg62-turbo \
    libssl-dev \
    libxext6 \
    xfonts-base \
    xfonts-75dpi \
    wget \
    xz-utils \
    && wget -O wkhtmltox.tar.xz https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.tar.xz \
    && tar -Jxf wkhtmltox.tar.xz -C /usr/local --strip-components 1 \
    && rm wkhtmltox.tar.xz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker's build cache.
# This layer only rebuilds if requirements.txt changes.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
# This layer rebuilds only when other code files change.
COPY . .

# Create the uploads directory.
RUN mkdir -p uploads

# Expose the application port.
EXPOSE 8000

# Command to run the application using Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
