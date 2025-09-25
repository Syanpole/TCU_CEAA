FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including OpenBLAS for scipy
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    gfortran \
    build-essential \
    pkg-config \
    cmake \
    python3-dev \
    libffi-dev \
    libssl-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for OpenBLAS discovery
ENV PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
ENV LD_LIBRARY_PATH="/usr/lib:/usr/local/lib:$LD_LIBRARY_PATH"

# Upgrade pip and install build tools first
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies in stages to avoid build conflicts
COPY requirements-ci.txt .
RUN pip install --no-cache-dir -r requirements-ci.txt --prefer-binary

# Install ML dependencies separately (may require compilation)
COPY requirements-ml.txt .
RUN pip install --no-cache-dir -r requirements-ml.txt --prefer-binary || \
    echo "Warning: Some ML packages failed to install, continuing without them"

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend_project.wsgi:application"]
