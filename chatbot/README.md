# LLM Chatbot with RAG and Guardrails

A secure chatbot implementation using LangGraph for pipeline orchestration, Guardrails-AI for security, and RAG for knowledge retrieval.

## Features

- **LangGraph Pipeline**: Structured workflow with input validation, context retrieval, LLM generation, and output validation
- **Guardrails Security**: Protection against prompt injection, toxic content, and PII exposure
- **RAG Integration**: Markdown document processing with semantic search
- **Flexible LLM Support**: OpenAI API and custom/private LLM endpoints
- **CLI Interface**: Simple stdin/stdout interaction

## Installation

### Option 1: Docker (Recommended for Testing)

1. Configure environment:
```bash
cp .env.example .env
# Edit .env with your LLM_API_KEY and configuration
```

2. Run with Docker:
```bash
./docker-test.sh
```

### Option 2: Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Add markdown documents to `data/documents/`

4. Initialize knowledge base:
```bash
python main.py --init-kb
```

## Usage

### Basic Chat
```bash
python main.py
```

### Knowledge Base Management
```bash
# Initialize knowledge base
python main.py --init-kb

# Show knowledge base info
python main.py --kb-info
```

## Configuration

### Environment Variables (.env)
- `LLM_PROVIDER`: openai, anthropic, or custom
- `LLM_API_KEY`: Your LLM API key
- `LLM_API_BASE_URL`: Custom endpoint URL (for private LLMs)
- `LLM_MODEL_NAME`: Model to use
- `LLM_CA_CERT_PATH`: Optional - Path to CA certificate file for self-signed certificates
- `EMBEDDING_MODEL`: Sentence transformer model
- `DOCUMENTS_PATH`: Path to markdown documents
- `GUARDRAILS_API_KEY`: Optional - Guardrails Hub API key for enhanced security
- `GUARDRAILS_ID`: Optional - Guardrails Hub ID for enhanced security

### Guardrails Security (Optional)
For enhanced security features, you can configure Guardrails:

1. **Get Guardrails Hub API credentials** from [Guardrails Hub](https://hub.guardrailsai.com/)
2. **Set environment variables** in your `.env` file:
   ```
   GUARDRAILS_API_KEY=your_api_key
   GUARDRAILS_ID=your_id
   ```
3. **Configure policies** in `config/guardrails.yaml`:
   - Prompt injection detection
   - Toxic language filtering
   - PII detection and anonymization
   - Output validation

**Note:** If Guardrails credentials are not provided, the chatbot will run with basic security measures and display warnings.

### Self-Hosted LLM Support

For self-hosted LLM servers with self-signed certificates:

1. **Place CA certificate** in the `certs/` directory
2. **Set environment variable**:
   ```
   LLM_CA_CERT_PATH=/app/certs/ca-cert.pem
   ```
3. **The chatbot will automatically**:
   - Set `REQUESTS_CA_BUNDLE` environment variable
   - Configure SSL verification for your custom endpoint

## Architecture

```
Input → Validation → Context Retrieval → LLM Generation → Output Validation → Response
```

Each node in the pipeline can be customized and extended as needed.

## Security Features

- Input validation and sanitization
- Prompt injection detection
- Toxic content filtering
- PII detection and anonymization
- Output validation and filtering