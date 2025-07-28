import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os

# Mock mode - don't import sentence_transformers
MOCK_MODE = True

class VectorStore:
    def __init__(self, collection_name: str = "knowledge_base", mock_mode: bool = False):
        self.collection_name = collection_name
        self.mock_mode = mock_mode or MOCK_MODE
        
        if not self.mock_mode:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                print("Warning: sentence-transformers not available, using mock mode")
                self.mock_mode = True
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Knowledge base for chatbot"}
            )
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """
        Add document chunks to vector store
        """
        if not chunks:
            return
        
        # Clear existing documents
        try:
            # Get all documents and delete them
            results = self.collection.get()
            if results['ids']:
                self.collection.delete(ids=results['ids'])
        except Exception as e:
            print(f"Warning: Could not clear existing documents: {e}")
        
        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []
        
        for chunk in chunks:
            ids.append(chunk["id"])
            texts.append(f"{chunk['key_path']}: {chunk['content']}")
            metadatas.append({
                "key_path": chunk["key_path"],
                "content": chunk["content"],
                "type": chunk["metadata"]["type"]
            })
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        """
        if self.mock_mode:
            return self._mock_search(query, top_k)
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        sources = []
        for i in range(len(results["ids"][0])):
            source = {
                "key_path": results["metadatas"][0][i]["key_path"],
                "content": results["metadatas"][0][i]["content"],
                "type": results["metadatas"][0][i]["type"],
                "distance": results["distances"][0][i]
            }
            sources.append(source)
        
        return sources
    
    def _mock_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Mock search that returns relevant chunks based on keywords
        """
        query_lower = query.lower()
        mock_sources = []
        
        # Mock data based on the sample_data.json
        mock_chunks = [
            {"key_path": "company_info.name", "content": "TechCorp Solutions", "type": "str"},
            {"key_path": "company_info.founded", "content": "2020", "type": "str"},
            {"key_path": "company_info.employee_count", "content": "150", "type": "int"},
            {"key_path": "company_info.revenue", "content": "$5.2M", "type": "str"},
            {"key_path": "products.0.name", "content": "CloudSync Pro", "type": "str"},
            {"key_path": "products.0.price", "content": "299.99", "type": "float"},
            {"key_path": "products.1.name", "content": "DataViz Analytics", "type": "str"},
            {"key_path": "products.1.price", "content": "499.99", "type": "float"},
            {"key_path": "team.ceo.name", "content": "Sarah Johnson", "type": "str"},
            {"key_path": "team.ceo.experience", "content": "15 years", "type": "str"},
            {"key_path": "customers.total", "content": "2500", "type": "int"},
            {"key_path": "customers.satisfaction_rate", "content": "94.5", "type": "float"}
        ]
        
        # Simple keyword matching
        for chunk in mock_chunks:
            if any(keyword in query_lower for keyword in ["company", "name", "techcorp"]) and "company_info.name" in chunk["key_path"]:
                mock_sources.append({"key_path": chunk["key_path"], "content": chunk["content"], "type": chunk["type"], "distance": 0.1})
            elif any(keyword in query_lower for keyword in ["employee", "employees", "how many"]) and "employee_count" in chunk["key_path"]:
                mock_sources.append({"key_path": chunk["key_path"], "content": chunk["content"], "type": chunk["type"], "distance": 0.1})
            elif any(keyword in query_lower for keyword in ["product", "price"]) and "price" in chunk["key_path"]:
                mock_sources.append({"key_path": chunk["key_path"], "content": chunk["content"], "type": chunk["type"], "distance": 0.2})
            elif "ceo" in query_lower and "ceo" in chunk["key_path"]:
                mock_sources.append({"key_path": chunk["key_path"], "content": chunk["content"], "type": chunk["type"], "distance": 0.1})
            elif "revenue" in query_lower and "revenue" in chunk["key_path"]:
                mock_sources.append({"key_path": chunk["key_path"], "content": chunk["content"], "type": chunk["type"], "distance": 0.1})
            elif "customer" in query_lower and "customer" in chunk["key_path"]:
                mock_sources.append({"key_path": chunk["key_path"], "content": chunk["content"], "type": chunk["type"], "distance": 0.1})
        
        return mock_sources[:top_k]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of vector store
        """
        try:
            count = self.collection.count()
            return {
                "loaded": count > 0,
                "document_count": 1 if count > 0 else 0,
                "chunks_count": count
            }
        except:
            return {
                "loaded": False,
                "document_count": 0,
                "chunks_count": 0
            }
    
    def clear(self):
        """
        Clear all documents from vector store
        """
        try:
            results = self.collection.get()
            if results['ids']:
                self.collection.delete(ids=results['ids'])
        except Exception as e:
            print(f"Warning: Could not clear documents: {e}") 