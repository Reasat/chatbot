# Minimal AWS Chatbot with RAG

## ✅ **COMPLETED: Minimal Working Example**

### **What We Built**

A clean, minimal chatbot application with:
- **AWS Titan Embeddings** for semantic search
- **AWS Bedrock LLM** for text generation
- **RAG Pipeline** for contextual responses
- **Document Upload** for knowledge base
- **Simple Frontend** for interaction

### **Architecture**

```
Frontend (Port 8080) ←→ FastAPI Backend (Port 8000) ←→ AWS Bedrock
                              ↓
                        In-Memory Vector Store
                              ↓
                        AWS Titan Embeddings
```

### **Key Features**

#### **✅ AWS Embeddings Working**
- Uses `amazon.titan-embed-text-v1` (1536 dimensions)
- Cosine similarity search
- In-memory storage (no ChromaDB complexity)

#### **✅ AWS Function Calls Working**
- Claude 3 Sonnet for text generation
- RAG pipeline with context injection
- Direct chat without RAG

#### **✅ Frontend Working**
- Document upload via drag & drop
- Chat interface with RAG toggle
- Response details and confidence scores
- Real-time status indicators

### **Files Structure**

```
chatbot/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── aws/
│   │   ├── bedrock_client.py    # AWS LLM client
│   │   └── embedding_client.py  # AWS embeddings
│   ├── rag/
│   │   ├── document_processor.py # JSON chunking
│   │   ├── vector_store.py       # In-memory vector store
│   │   └── retrieval.py          # RAG pipeline
│   └── requirements.txt
├── frontend/
│   ├── index.html          # Chat interface
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── run.sh                  # Start script
├── setup.sh                # Setup script
└── sample_data.json        # Test data
```

### **How to Use**

1. **Setup**
   ```bash
   bash setup.sh
   ```

2. **Configure AWS**
   ```bash
   cp backend/env.example backend/.env
   # Edit with your AWS credentials
   ```

3. **Start Backend**
   ```bash
   bash run.sh
   ```

4. **Start Frontend**
   ```bash
   cd frontend && python -m http.server 8080
   ```

5. **Test**
   ```bash
   python test_minimal.py
   ```

### **API Endpoints**

- `GET /health` - Health check
- `POST /upload-knowledge-base` - Upload JSON
- `GET /knowledge-base-status` - Get status
- `POST /chat` - Chat with RAG

### **What Was Removed**

- ❌ ChromaDB complexity
- ❌ Local sentence-transformers
- ❌ Multiple embedding modes
- ❌ Complex configuration files
- ❌ Extensive documentation
- ❌ Mock mode switching scripts

### **What Was Kept**

- ✅ AWS Titan embeddings
- ✅ AWS Bedrock LLM calls
- ✅ RAG pipeline
- ✅ Document upload
- ✅ Frontend interface
- ✅ Simple in-memory storage

### **Testing**

The application has been tested to ensure:
- ✅ AWS embeddings generate correctly
- ✅ AWS function calls work
- ✅ RAG pipeline retrieves relevant documents
- ✅ Frontend uploads and displays documents
- ✅ Chat interface works with RAG toggle

### **Ready for Production**

This minimal example is:
- **Clean**: No unnecessary code
- **Focused**: Only AWS embeddings and LLM
- **Working**: All features tested and functional
- **Simple**: Easy to understand and modify

**Status**: ✅ **READY TO USE** 