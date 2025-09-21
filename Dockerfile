# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Environment variables (can be overridden at runtime)
ENV REDIRECT_URL=http://localhost:8080/webhook
ENV LISTEN_PORT=5000
ENV HOST=0.0.0.0
ENV DEBUG=False

# Run the application
CMD ["python", "app.py"]