FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install system dependencies and Mermaid CLI in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        nodejs \
        npm \
        fontconfig && \
    npm install -g @mermaid-js/mermaid-cli && \
    npm cache clean --force && \
    apt-get remove -y npm && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* \
           /root/.npm \
           /tmp/* \
           /var/tmp/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile -r requirements.txt && \
    pip cache purge

# Copy application code
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

