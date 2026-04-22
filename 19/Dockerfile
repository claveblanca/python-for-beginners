# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies first — this layer is cached
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source — changes here don't invalidate the pip layer
COPY . .

EXPOSE 7860
ENV SERVER_PORT=7860
ENV LOG_LEVEL=INFO

CMD ["python", "main.py"]
