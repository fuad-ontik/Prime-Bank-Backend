# Use official Python image
FROM python:3.11-slim

# Install curl for testing
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY data/ ./data/
COPY test.sh /app/test.sh

# Expose port for Cloud Run
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=app/main.py

RUN chmod +x /app/test.sh

# Start the app with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app.main:app"]
# CMD ["./test.sh"]