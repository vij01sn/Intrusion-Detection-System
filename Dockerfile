FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the application files to the container
COPY . .

# Expose port (Render sets this dynamically via the PORT environment variable)
EXPOSE 5000

# Run the Flask app using python
CMD ["python", "app.py"]
