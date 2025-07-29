# AWS Chatbot with RAG

A minimal chatbot application with RAG (Retrieval-Augmented Generation) using AWS Bedrock for both embeddings and LLM calls.

## Features

- **AWS Titan Embeddings**: High-quality embeddings using `amazon.titan-embed-text-v1`
- **AWS Bedrock LLM**: Claude 3 Sonnet for text generation
- **RAG Pipeline**: Retrieve relevant documents and generate contextual responses
- **Document Upload**: Upload JSON documents for knowledge base
- **Simple Vector Store**: In-memory storage with cosine similarity search

## Quick Start

**Prerequisites**: Python 3.11+ installed on your system

1. **Setup environment**
   ```bash
   bash setup.sh
   ```

2. **Configure AWS credentials (optional)**
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env with your AWS credentials
   ```

3. **Start the application**
   ```bash
   bash run.sh
   ```

4. **Open frontend**
   ```bash
   cd frontend && python -m http.server 8080
   ```
   Visit: http://localhost:8080

## Usage

1. **Upload Knowledge Base**: Drag and drop a JSON file
2. **Chat with RAG**: Ask questions about your data
3. **Toggle RAG**: Enable/disable knowledge base usage

## API Endpoints

- `GET /health` - Health check
- `POST /upload-knowledge-base` - Upload JSON document
- `GET /knowledge-base-status` - Get status
- `POST /chat` - Chat with RAG

## Architecture

```
Frontend ←→ FastAPI Backend ←→ AWS Bedrock (LLM)
                    ↓
              AWS Titan Embeddings
                    ↓
              In-Memory Vector Store
```

## Requirements

- AWS Bedrock access
- Python 3.11+
- AWS credentials in `backend/.env` (optional for mock mode)

## Troubleshooting

### AWS Credential Errors
If you see errors like "The security token included in the request is invalid":

1. **Use Mock Mode**: The application automatically falls back to mock mode when AWS credentials are not configured
2. **Configure AWS Credentials**: 
   ```bash
   cp backend/env.example backend/.env
   # Add your AWS credentials:
   # AWS_ACCESS_KEY_ID=your_access_key
   # AWS_SECRET_ACCESS_KEY=your_secret_key
   # AWS_REGION=us-east-1
   ```
3. **Verify AWS Bedrock Access**: Ensure you have access to Bedrock models in your AWS console

### Verify Setup
Run the verification script to test your setup:
```bash
python verify_setup.py
``` 
