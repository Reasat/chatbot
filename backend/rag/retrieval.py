from typing import List, Dict, Any, Tuple
from rag.vector_store import VectorStore
from aws.bedrock_client import BedrockClient

class RAGPipeline:
    def __init__(self, vector_store: VectorStore, bedrock_client: BedrockClient):
        self.vector_store = vector_store
        self.bedrock_client = bedrock_client
    
    async def process_query(self, query: str) -> Tuple[str, List[Dict[str, Any]], float]:
        """
        Process query using RAG pipeline
        Returns: (response, sources, confidence)
        """
        # Retrieve relevant documents
        sources = self.vector_store.search(query, top_k=5)
        
        if not sources:
            # No relevant sources found, use direct generation
            response = await self.bedrock_client.generate_response(query)
            return response, [], 0.5
        
        # Build context from sources
        context = self._build_context(sources)
        
        # Calculate confidence based on source relevance
        confidence = self._calculate_confidence(sources)
        
        # Generate response with context
        response = await self._generate_with_context(query, context, sources)
        
        return response, sources, confidence
    
    def _build_context(self, sources: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved sources
        """
        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(f"{i}. {source['key_path']}: {source['content']}")
        
        return "\n".join(context_parts)
    
    def _calculate_confidence(self, sources: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score based on source relevance
        """
        if not sources:
            return 0.0
        
        # Average distance (lower is better)
        avg_distance = sum(source["distance"] for source in sources) / len(sources)
        
        # Convert distance to confidence (0-1 scale)
        # Assuming distances are typically 0-2, with 0 being perfect match
        confidence = max(0.0, min(1.0, 1.0 - avg_distance / 2.0))
        
        return confidence
    
    async def _generate_with_context(self, query: str, context: str, sources: List[Dict[str, Any]]) -> str:
        """
        Generate response using context and sources
        """
        prompt = f"""You are a helpful assistant that answers questions based on the provided knowledge base.

Knowledge Base Context:
{context}

User Question: {query}

Please answer the question based on the knowledge base context above. If the information is not available in the context, say so clearly. Be concise and accurate.

Answer:"""
        
        response = await self.bedrock_client.generate_response(prompt)
        return response 