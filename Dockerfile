# Start with a minimal base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies (copy and install requirements in a single layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH /app:$PYTHONPATH
ENV AM_I_IN_A_DOCKER_CONTAINER=Yes

# Copy application files
COPY . .

CMD ["sh", "-c", "python bot/bot_main.py"]