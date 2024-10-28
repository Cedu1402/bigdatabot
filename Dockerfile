# Start with a minimal base image
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Install dependencies (copy and install requirements in a single layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Copy application files
COPY . .

# Run the application
CMD ["python", "main.py"]
