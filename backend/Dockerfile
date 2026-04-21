FROM python:3.12-slim

WORKDIR /app

# System dependencies (minimal set for Cloud Run CPU-only)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch FIRST (prevents downloading 900MB CUDA libraries)
RUN pip install --no-cache-dir \
    torch==2.5.1 \
    torchvision==0.20.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Install base Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install opencv-python-headless BEFORE ultralytics
RUN pip install --no-cache-dir opencv-python-headless==4.10.0.84

# Install ultralytics with --no-deps to prevent opencv-python installation
RUN pip install --no-cache-dir --no-deps ultralytics==8.3.0

# Copy project
COPY . .

# Copy and set permissions for entrypoint and migration scripts
COPY entrypoint.sh /app/entrypoint.sh
COPY migrate.sh /app/migrate.sh
RUN chmod +x /app/entrypoint.sh /app/migrate.sh

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
