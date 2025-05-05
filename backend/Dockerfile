# Dockerfile

# 1) Start from a lightweight Python 3.11 base
FROM python:3.11-slim

# 2) Create a working directory inside the container
WORKDIR /app

# 3) Copy requirements.txt first for caching
COPY requirements.txt /app/

# 4) Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5) Pre-download the cross-encoder model during build
#    This ensures no large downloads at runtime.
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# 6) Copy all backend code (app.py, etc.) into the container
COPY . /app

# 7) Expose the FastAPI port (8000)
EXPOSE 8000

# 8) Default command: run uvicorn on port 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
