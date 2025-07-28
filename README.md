# Chatbot

A modern chatbot application with RAG (Retrieval-Augmented Generation) capabilities, built with FastAPI, AWS Bedrock, and a beautiful vanilla JavaScript frontend.

**Built with CursorAI** - This repository was developed using CursorAI. It is designed to serve as a chatbot template for building RAG-powered applications.

## Features

### AI-Powered Chat
- Real-time chat interface with AWS Bedrock integration
- Support for Claude 3 Sonnet model
- Toggle between RAG and direct AI responses

### Knowledge Base Management
- Upload JSON documents as knowledge base
- Automatic chunking by JSON keys
- Vector storage with ChromaDB
- Semantic search for relevant context

### RAG Pipeline
- Document retrieval using sentence transformers
- Context-aware responses
- Source attribution and confidence scoring
- Processing time tracking

### Modern UI
- Beautiful, responsive chat interface
- Drag-and-drop file upload
- Real-time status indicators
- Detailed response analytics

## Architecture

```
Frontend (Vanilla JS) ←→ FastAPI Backend ←→ AWS Bedrock
                              ↓
                        ChromaDB (Vector Store)
                              ↓
                    Sentence Transformers (Embeddings)
```

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **AWS Account with Bedrock Access** (optional for mock mode)
3. **AWS Credentials configured** (optional for mock mode)

### Installation

1. **Setup environment and install dependencies:**
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup script
bash setup.sh
```

2. **Configure AWS credentials (optional for production):**
```bash
# Option 1: Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# Option 2: Create .env file
cp backend/env.example backend/.env
# Edit backend/.env with your credentials
```

3. **Start the application:**
```bash
# Make run script executable
chmod +x run.sh

# Start the backend
bash run.sh
```

4. **Open frontend:**
```bash
# Open frontend/index.html in your browser
# Or serve with a simple HTTP server:
cd frontend && python -m http.server 8080
# Then visit http://localhost:8080/
```

## Usage

### 1. Upload Knowledge Base
- Drag and drop a JSON file or click to browse
- The system will automatically chunk the JSON by keys
- Each key-value pair becomes a searchable chunk

### 2. Chat with RAG
- Toggle "Use Knowledge Base" to enable/disable RAG
- Ask questions about your uploaded data
- View source attribution and confidence scores

### 3. Response Details
- Click "View details" on any response
- See which JSON keys were used
- Check confidence scores and processing time

## API Endpoints

### `POST /upload-knowledge-base`
Upload JSON knowledge base document
- **Input**: JSON file
- **Output**: Knowledge base status

### `GET /knowledge-base-status`
Get current knowledge base status
- **Output**: Loaded status and chunk count

### `POST /chat`
Process chat message
- **Input**: `{"message": "string", "use_rag": boolean}`
- **Output**: `{"response": "string", "sources": [...], "confidence": float, "processing_time": float}`

### `GET /health`
Health check endpoint

## JSON Chunking Strategy

The system chunks JSON documents by keys:

```json
{
  "company_info": {
    "name": "TechCorp",
    "founded": "2020"
  },
  "products": [
    {"name": "Product A", "price": 100}
  ]
}
```

Becomes chunks:
- `company_info.name: TechCorp`
- `company_info.founded: 2020`
- `products.0.name: Product A`
- `products.0.price: 100`

## Configuration

### Environment Variables
- `AWS_ACCESS_KEY_ID`: Your AWS access key (optional for mock mode)
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key (optional for mock mode)
- `AWS_REGION`: AWS region (default: us-east-1)

### Model Configuration
- Default: Claude 3 Sonnet
- Configurable in `backend/aws/bedrock_client.py`
- Mock mode available for testing without AWS credentials

## Development

### Backend Structure
```
backend/
├── main.py              # FastAPI application
├── rag/
│   ├── document_processor.py  # JSON chunking
│   ├── vector_store.py        # ChromaDB operations
│   └── retrieval.py           # RAG pipeline
├── aws/
│   └── bedrock_client.py      # AWS Bedrock client
└── requirements.txt
```

### Frontend Structure
```
frontend/
├── index.html          # Main interface
├── style.css           # Modern styling
└── script.js           # Interactive functionality
```

## Features in Detail

### RAG Pipeline
1. **Query Processing**: User question is embedded
2. **Retrieval**: Semantic search finds relevant JSON chunks
3. **Context Building**: Retrieved chunks form context
4. **Generation**: Bedrock generates response with context
5. **Attribution**: Sources and confidence are tracked

### Vector Storage
- **Database**: ChromaDB (local, persistent)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Search**: Top-k retrieval with distance scoring

### Response Analytics
- **Confidence**: Based on source relevance scores
- **Sources**: Which JSON keys were used
- **Processing Time**: End-to-end response time

### Mock Mode
- **No AWS Required**: Works without AWS credentials
- **Pre-defined Responses**: Based on keyword matching
- **Fast Processing**: Instant responses for testing
- **Easy Development**: No costs or setup required

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   - Ensure AWS credentials are properly configured (for production mode)
   - Check Bedrock access permissions
   - Use mock mode for testing without AWS

2. **ChromaDB Issues**
   - Delete `chroma_db` folder to reset vector store
   - Check disk space for embeddings

3. **Frontend Connection**
   - Ensure backend is running on port 8000
   - Check CORS settings if needed

### Performance Tips

1. **Large JSON Files**
   - Consider chunking strategy for very large documents
   - Monitor memory usage during processing

2. **Response Time**
   - Embeddings are cached after first load
   - Consider model selection for speed vs quality

## Future Enhancements

- [ ] Multiple knowledge base support
- [ ] Real-time streaming responses
- [ ] Advanced chunking strategies
- [ ] User authentication
- [ ] Response history persistence
- [ ] Export functionality
- [ ] Mobile app version

## License

Apache 2.0 License - feel free to use and modify as needed. 
