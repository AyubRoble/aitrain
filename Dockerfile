FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all files
COPY . .

# Make sure the files exist
RUN ls -la

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]