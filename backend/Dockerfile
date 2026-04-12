FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 git && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app /app/app

# We mount /app/storage and /app/models via docker-compose

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
