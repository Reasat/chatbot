import json
from typing import List, Dict, Any
import os
from aws.embedding_client import AWSBedrockEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.documents = []
        self.embeddings = []
        
        if not mock_mode:
            try:
                self.embedding_model = AWSBedrockEmbeddings(mock_mode=False)
                print("✅ Using AWS Titan embeddings")
            except Exception as e:
                print(f"Warning: AWS embedding client not available, using mock mode: {e}")
                self.mock_mode = True
        
        if self.mock_mode:
            self.embedding_model = AWSBedrockEmbeddings(mock_mode=True)
            print("✅ Using mock embeddings")
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Add document chunks to vector store"""
        if not chunks:
            return
        
        # Clear existing documents
        self.documents = []
        self.embeddings = []
        
        # Process chunks
        for chunk in chunks:
            text = f"{chunk['key_path']}: {chunk['content']}"
            embedding = self.embedding_model.embed_text(text)
            
            self.documents.append({
                "id": chunk["id"],
                "text": text,
                "key_path": chunk["key_path"],
                "content": chunk["content"],
                "type": chunk["metadata"]["type"]
            })
            self.embeddings.append(embedding)
        
        print(f"✅ Added {len(chunks)} documents to vector store")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using cosine similarity"""
        if not self.documents:
            return []
        
        # Get query embedding
        query_embedding = self.embedding_model.embed_text(query)
        
        # Calculate similarities
        similarities = []
        for doc_embedding in self.embeddings:
            similarity = cosine_similarity([query_embedding], [doc_embedding])[0][0]
            similarities.append(similarity)
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        sources = []
        for idx in top_indices:
            doc = self.documents[idx]
            sources.append({
                "key_path": doc["key_path"],
                "content": doc["content"],
                "type": doc["type"],
                "distance": 1 - similarities[idx]  # Convert similarity to distance
            })
        
        return sources
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of vector store"""
        return {
            "loaded": len(self.documents) > 0,
            "document_count": 1 if len(self.documents) > 0 else 0,
            "chunks_count": len(self.documents),
            "embedding_type": "AWS Titan" if not self.mock_mode else "Mock",
            "mock_mode": self.mock_mode
        }
    
    def clear(self):
        """Clear all documents from vector store"""
        self.documents = []
        self.embeddings = [] 