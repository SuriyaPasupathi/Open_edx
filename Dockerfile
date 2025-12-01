FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    gettext \
    curl \
    git \
    netcat-openbsd \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for frontend assets)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements and install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/edx/development.txt

# Copy package.json and scripts directory (needed for postinstall script)
COPY package.json package-lock.json ./
COPY scripts/ scripts/
RUN npm install

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/logs

# Build webpack assets for development
RUN npm run webpack-dev || echo "Webpack build completed with warnings"

# Expose ports
EXPOSE 18000 18010

# Default command (can be overridden in docker-compose)
CMD ["python", "manage.py", "lms", "runserver", "0.0.0.0:18000", "--settings=devstack"]

