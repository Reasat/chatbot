from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from dotenv import load_dotenv

from rag.document_processor import DocumentProcessor
from rag.vector_store import VectorStore
from rag.retrieval import RAGPipeline
from aws.bedrock_client import BedrockClient

load_dotenv()

app = FastAPI(title="Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For POC, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
vector_store = VectorStore(mock_mode=True)  # Use mock mode for testing
bedrock_client = BedrockClient(mock_mode=True)  # Use mock mode for testing
rag_pipeline = RAGPipeline(vector_store, bedrock_client)

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]
    confidence: float
    processing_time: float

class KnowledgeBaseStatus(BaseModel):
    loaded: bool
    document_count: int
    chunks_count: int

@app.get("/")
async def root():
    return {"message": "Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload-knowledge-base", response_model=KnowledgeBaseStatus)
async def upload_knowledge_base(file: UploadFile = File(...)):
    """Upload JSON knowledge base document"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and parse JSON
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
        
        # Process document into chunks
        chunks = document_processor.process_json(json_data)
        
        # Store in vector database
        vector_store.add_documents(chunks)
        
        return KnowledgeBaseStatus(
            loaded=True,
            document_count=1,
            chunks_count=len(chunks)
        )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/knowledge-base-status", response_model=KnowledgeBaseStatus)
async def get_knowledge_base_status():
    """Get current knowledge base status"""
    try:
        status = vector_store.get_status()
        return KnowledgeBaseStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message with optional RAG"""
    try:
        import time
        start_time = time.time()
        
        if request.use_rag:
            # Use RAG pipeline
            response, sources, confidence = await rag_pipeline.process_query(request.message)
        else:
            # Direct Bedrock call
            response = await bedrock_client.generate_response(request.message)
            sources = []
            confidence = 1.0
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=response,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 