# Challenge_1a/Dockerfile
FROM python:3.10-slim

# Prevent .pyc files & force unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy your processing script and the schema
COPY process_pdfs.py .
COPY sample_dataset/schema sample_dataset/schema

# 3) Prepare the input/output mountpoints and symlinks
RUN mkdir -p /app/input /app/output \
 && mkdir -p sample_dataset/pdfs sample_dataset/outputs \
 && ln -sf /app/input  sample_dataset/pdfs \
 && ln -sf /app/output sample_dataset/outputs

# 4) When the container starts, run your script
ENTRYPOINT ["python", "process_pdfs.py"]
