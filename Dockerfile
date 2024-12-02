# Start with a minimal base image
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    make \
    libffi-dev \
    openblas-dev \
    lapack-dev \
    python3-dev

# Install dependencies (copy and install requirements in a single layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 -r requirements.txt && rm requirements.txt

# Copy application files
COPY . .

# Run the application
CMD ["python", "./bot/main.py"]
