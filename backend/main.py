from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import logging
from dotenv import load_dotenv

from rag.document_processor import DocumentProcessor
from rag.vector_store import VectorStore
from rag.retrieval import RAGPipeline
from aws.bedrock_client import BedrockClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chatbot.log')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
logger.info("Initializing chatbot components...")
document_processor = DocumentProcessor()
vector_store = VectorStore(mock_mode=False)  # Use AWS Titan embeddings
bedrock_client = BedrockClient(mock_mode=False)  # Use real AWS Bedrock
rag_pipeline = RAGPipeline(vector_store, bedrock_client)
logger.info("Chatbot components initialized successfully")

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]
    confidence: float
    processing_time: float

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy", "message": "Chatbot API is running"}

@app.post("/upload-knowledge-base")
async def upload_knowledge_base(file: UploadFile = File(...)):
    """Upload and process JSON knowledge base"""
    logger.info(f"Knowledge base upload started: {file.filename}")
    try:
        # Read file content
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
        logger.info(f"JSON file loaded successfully, size: {len(content)} bytes")
        
        # Process JSON into chunks
        logger.info("Processing JSON into chunks...")
        chunks = document_processor.process_json(json_data)
        logger.info(f"JSON processed into {len(chunks)} chunks")
        
        # Log each chunk being indexed
        for i, chunk in enumerate(chunks):
            logger.info(f"Indexing chunk {i+1}/{len(chunks)}: {chunk['key_path']} - Content: {chunk['content'][:100]}{'...' if len(chunk['content']) > 100 else ''}")
        
        # Add to vector store
        logger.info("Adding chunks to vector store...")
        vector_store.add_documents(chunks)
        logger.info(f"Successfully indexed {len(chunks)} chunks in vector store")
        
        return {
            "message": f"Knowledge base uploaded successfully",
            "chunks_processed": len(chunks),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/knowledge-base-status")
async def get_knowledge_base_status():
    """Get current knowledge base status"""
    logger.info("Knowledge base status requested")
    status = vector_store.get_status()
    logger.info(f"Knowledge base status: {status}")
    return status

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message with optional RAG"""
    logger.info(f"Chat request received: '{request.message[:50]}{'...' if len(request.message) > 50 else ''}' (RAG: {request.use_rag})")
    try:
        import time
        start_time = time.time()
        
        if request.use_rag:
            # Use RAG pipeline
            logger.info("Processing query with RAG pipeline...")
            response, sources, confidence = await rag_pipeline.process_query(request.message)
            logger.info(f"RAG processing complete. Retrieved {len(sources)} sources, confidence: {confidence:.3f}")
            
            # Log retrieved chunks
            for i, source in enumerate(sources):
                logger.info(f"Retrieved source {i+1}/{len(sources)}: {source['key_path']} - Content: {source['content'][:100]}{'...' if len(source['content']) > 100 else ''}")
        else:
            # Direct Bedrock call
            logger.info("Processing query with direct Bedrock call...")
            response = await bedrock_client.generate_response(request.message)
            sources = []
            confidence = 1.0
            logger.info("Direct Bedrock call complete")
        
        processing_time = time.time() - start_time
        logger.info(f"Chat processing completed in {processing_time:.3f} seconds")
        
        return ChatResponse(
            response=response,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 