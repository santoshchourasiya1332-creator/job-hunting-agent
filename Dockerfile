FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# System dependencies update and install required browser/PDF libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libgobject-2.0-0 \
    libexpat1 \
    libfontconfig1 \
    libfreetype6 \
    libxi6 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies from app folder (ensure playwright==1.40.0 in requirements.txt)
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy full code structure
COPY app/ .

CMD ["python", "main.py"]