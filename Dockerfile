FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip

# Install numpy first
RUN pip install --no-cache-dir numpy==1.24.3

# Then install scikit-learn
RUN pip install --no-cache-dir scikit-learn==1.3.0

# Copy requirements and install remaining packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT