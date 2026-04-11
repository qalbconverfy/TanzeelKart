FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
gcc \
libpq-dev \
&& rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Run
CMD ["gunicorn", "app.main:app", \
"--worker-class", "uvicorn.workers.UvicornWorker", \
"--workers", "4", \
"--bind", "0.0.0.0:8000", \
"--timeout", "120", \
"--access-logfile", "-", \
"--error-logfile", "-"]