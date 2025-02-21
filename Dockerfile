FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32
CMD uvicorn main:app --host 0.0.0.0 --port $PORT