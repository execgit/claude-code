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
- `EMBEDDING_MODEL`: Sentence transformer model
- `DOCUMENTS_PATH`: Path to markdown documents

### Guardrails (config/guardrails.yaml)
Configure security policies for:
- Prompt injection detection
- Toxic language filtering
- PII detection and anonymization
- Output validation

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