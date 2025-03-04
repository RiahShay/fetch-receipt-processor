FROM python:3.8

# Set working directory to /app
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . /app

# Set the PYTHONPATH environment variable to include the app folder
ENV PYTHONPATH=/app

# Set PYTHONPATH for both local and Docker environments
ENV PYTHONPATH=/app:$PYTHONPATH

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
