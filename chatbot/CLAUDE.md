# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Basic chat interface
python main.py

# Initialize knowledge base from documents in data/documents/
python main.py --init-kb

# Show knowledge base information
python main.py --kb-info

# IRC mode (get messages from IRC instead of command line)
python main.py --irc-mode

# Usage and security reports
python main.py --usage-report --hours 24
python main.py --security-report --hours 24
```

### Docker Development
```bash
# Build and run with Docker (recommended for testing)
./docker-test.sh

# Manual Docker commands
docker build -t llm-chatbot .
docker compose --profile init up chatbot-init  # Initialize KB
docker compose run --rm chatbot python3 main.py
```

### Code Quality
```bash
# Formatting and linting (based on pyproject.toml configuration)
black .
isort .
flake8
mypy .
```

### Testing
```bash
# Run comprehensive validator testing harness (no mocks, real validation)
python test_validator_harness.py

# Run concurrent performance tests
python test_validator_harness.py --concurrent

# Save detailed results to file
python test_validator_harness.py --output validation_report.json

# Run with custom configuration
python test_validator_harness.py --config custom_test_config.yaml

# Quiet mode (minimal output)
python test_validator_harness.py --quiet
```

## Architecture Overview

This is a secure LLM chatbot built with a **LangGraph pipeline architecture** for structured workflow orchestration. The system implements comprehensive security through Guardrails-AI and provides knowledge retrieval via RAG.

### Core Pipeline Flow
The chatbot processes requests through a 4-stage LangGraph pipeline:
```
Input → Validation → Context Retrieval → LLM Generation → Output Validation → Response
```

### Key Components

**Pipeline (`src/pipeline/`)**
- `graph.py`: LangGraph workflow definition with `ChatbotState` and conditional routing
- `nodes.py`: Individual pipeline nodes (validation, retrieval, generation, output validation)

**Security (`src/security/`)**
- `guards.py`: Guardrails-AI integration for input/output validation
- `unusual_prompt.py`: Custom unusual prompt detection validator
- Multi-layered protection: prompt injection detection, toxic content filtering, PII detection

**RAG System (`src/rag/`)**
- `documents.py`: Markdown document processing and chunking
- `embeddings.py`: Sentence transformer embeddings with ChromaDB
- `retrieval.py`: Semantic search and context retrieval

**Utils (`src/utils/`)**
- `logging.py`: Structured logging with file rotation
- `metrics.py`: Token usage and security event tracking
- `irc.py`: IRC bot integration for alternative input method
- `guardrails_setup.py`: Guardrails configuration management

### State Management
The system uses `ChatbotState` TypedDict with fields:
- `user_input`, `validated_input`, `context`, `llm_response`, `response`, `error`

### Configuration
- **Environment**: `.env` file with LLM provider settings, API keys, model configuration
- **Security**: `config/guardrails.yaml` for security policies and validation rules
- **Settings**: `config/settings.py` for application configuration management

### LLM Provider Support
Flexible LLM integration supporting OpenAI API, Anthropic, and custom/private LLM endpoints with SSL certificate handling for self-hosted deployments.

### Knowledge Base
Documents in `data/documents/` are processed into ChromaDB vector store (`data/vectordb/`) for semantic retrieval. Knowledge base requires initialization via `--init-kb` flag.

### Security Features
- Input validation and sanitization
- Prompt injection detection via DetectJailbreak validator
- Custom unusual prompt detection
- Output validation and filtering
- Comprehensive logging of security events

### Validator Testing Framework
The `test_validator_harness.py` provides comprehensive testing of all input validation components:

**Tested Validators:**
- `SecurityGuards`: Main security validation system with Guardrails-AI integration
- `UnusualPrompt`: Custom LLM-based unusual prompt detection validator  
- `ChatbotPipeline`: Complete pipeline input validation node testing

**Test Categories:** 80+ test cases across 8 categories:
- `benign_inputs`: Normal user queries that should pass validation
- `jailbreak_attempts`: Prompt injection and system override attempts 
- `unusual_prompts`: Suspicious requests including Kouvosto triggers
- `prompt_injections`: Advanced injection techniques and bypasses
- `backdoor_tests`: Tests for the TouchYerSpaget backdoor vulnerability
- `edge_cases`: Empty strings, unicode, multiline, control characters
- `length_tests`: Various input lengths from short to over-limit
- `security_tests`: SQL injection, XSS, command injection patterns

**Configuration:** 
- Automatically falls back to production environment variables (e.g., `LLM_PROVIDER`) when test-specific ones (e.g., `TEST_LLM_PROVIDER`) aren't set
- Supports custom YAML configuration files
- Configurable retry attempts, timeouts, and concurrency

**Reports:**
- Detailed accuracy metrics by validator and category
- Performance timing analysis  
- False positive/negative identification
- Security vulnerability detection with exit codes (0=success, 1=error, 2=vulnerabilities found)
- JSON/YAML export support

The codebase follows Python 3.11 standards with Black formatting (88 char line length), isort import organization, and mypy type checking configured in pyproject.toml.