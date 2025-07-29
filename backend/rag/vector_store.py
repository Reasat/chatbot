import json
from typing import List, Dict, Any
import os
import logging
from aws.embedding_client import AWSBedrockEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.documents = []
        self.embeddings = []
        
        if not mock_mode:
            try:
                self.embedding_model = AWSBedrockEmbeddings(mock_mode=False)
                logger.info("✅ Using AWS Titan embeddings")
            except Exception as e:
                logger.warning(f"Warning: AWS embedding client not available, using mock mode: {e}")
                self.mock_mode = True
        
        if self.mock_mode:
            self.embedding_model = AWSBedrockEmbeddings(mock_mode=True)
            logger.info("✅ Using mock embeddings")
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Add document chunks to vector store"""
        if not chunks:
            return
        
        logger.info(f"Adding {len(chunks)} documents to vector store...")
        
        # Clear existing documents
        self.documents = []
        self.embeddings = []
        
        # Process chunks
        for i, chunk in enumerate(chunks):
            text = f"{chunk['key_path']}: {chunk['content']}"
            logger.info(f"Generating embedding for chunk {i+1}/{len(chunks)}: {chunk['key_path']}")
            embedding = self.embedding_model.embed_text(text)
            logger.info(f"Embedding generated for chunk {i+1}, dimensions: {len(embedding)}")
            
            self.documents.append({
                "id": chunk["id"],
                "text": text,
                "key_path": chunk["key_path"],
                "content": chunk["content"],
                "type": chunk["metadata"]["type"]
            })
            self.embeddings.append(embedding)
        
        logger.info(f"✅ Added {len(chunks)} documents to vector store")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using cosine similarity"""
        if not self.documents:
            logger.info("No documents in vector store, returning empty results")
            return []
        
        logger.info(f"Searching for query: '{query[:50]}{'...' if len(query) > 50 else ''}' (top_k: {top_k})")
        
        # Get query embedding
        logger.info("Generating query embedding...")
        query_embedding = self.embedding_model.embed_text(query)
        logger.info(f"Query embedding generated, dimensions: {len(query_embedding)}")
        
        # Calculate similarities
        logger.info(f"Calculating similarities against {len(self.embeddings)} documents...")
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = cosine_similarity([query_embedding], [doc_embedding])[0][0]
            similarities.append(similarity)
            logger.info(f"Document {i+1} similarity: {similarity:.4f}")
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        logger.info(f"Top {len(top_indices)} results selected")
        
        sources = []
        for i, idx in enumerate(top_indices):
            doc = self.documents[idx]
            similarity = similarities[idx]
            logger.info(f"Result {i+1}: {doc['key_path']} (similarity: {similarity:.4f})")
            sources.append({
                "key_path": doc["key_path"],
                "content": doc["content"],
                "type": doc["type"],
                "distance": 1 - similarity  # Convert similarity to distance
            })
        
        logger.info(f"Search completed, returning {len(sources)} results")
        return sources
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of vector store"""
        status = {
            "loaded": len(self.documents) > 0,
            "document_count": 1 if len(self.documents) > 0 else 0,
            "chunks_count": len(self.documents),
            "embedding_type": "AWS Titan" if not self.mock_mode else "Mock",
            "mock_mode": self.mock_mode
        }
        logger.info(f"Vector store status: {status}")
        return status
    
    def clear(self):
        """Clear all documents from vector store"""
        logger.info("Clearing all documents from vector store")
        self.documents = []
        self.embeddings = [] 