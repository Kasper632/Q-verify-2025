FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy the AI models into the container
COPY AI-models /app/AI-models

# Expose the Flask app port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]