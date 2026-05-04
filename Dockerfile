FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Render sets PORT dynamically; default to 5000 locally
EXPOSE 5000

# Use shell form so $PORT env variable is properly expanded by Render
CMD sh -c "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120"