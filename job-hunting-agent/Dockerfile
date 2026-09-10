FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# System dependencies update
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies from app folder
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries inside container
RUN playwright install chromium

# Copy full code structure
COPY app/ .

CMD ["python", "main.py"]