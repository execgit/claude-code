FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Preload punkt tokenizer
ADD https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip /root/
RUN mkdir -p /root/nltk_data/tokenizers && unzip /root/punkt.zip -d /root/nltk_data/tokenizers && rm /root/punkt.zip

# Preload models. Different scripts use different libraries for the
# same models, maybe we should refactor
RUN python -c "from transformers import pipeline, AutoTokenizer, AutoModel; \
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2'); \
AutoModel.from_pretrained('GuardrailsAI/prompt-saturation-attack-detector'); \
AutoTokenizer.from_pretrained('google-bert/bert-base-cased'); \
AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
pipeline('text-classification', 'zhx123/ftrobertallm'); \
pipeline('text-classification', \
	 'madhurjindal/autonlp-Gibberish-Detector-492513457')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/vectordb

# Copy and install custom CA certificates if they exist
COPY certs/*.crt /usr/local/share/ca-certificates/

# Update CA certificates (will only run if certificates were copied)
RUN update-ca-certificates

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Expose port (if needed for future web interface)
#EXPOSE 8000

# Default command to run the chatbot
CMD ["python", "main.py"]