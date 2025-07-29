from typing import List, Dict, Any, Tuple
import logging
from rag.vector_store import VectorStore
from aws.bedrock_client import BedrockClient

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, vector_store: VectorStore, bedrock_client: BedrockClient):
        self.vector_store = vector_store
        self.bedrock_client = bedrock_client
        logger.info("RAG Pipeline initialized")
    
    async def process_query(self, query: str) -> Tuple[str, List[Dict[str, Any]], float]:
        """Process query using RAG pipeline"""
        logger.info(f"RAG pipeline processing query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        # Retrieve relevant documents
        logger.info("Retrieving relevant documents from vector store...")
        sources = self.vector_store.search(query, top_k=5)
        logger.info(f"Retrieved {len(sources)} sources from vector store")
        
        if not sources:
            logger.warning("No relevant sources found, using direct generation")
            # No relevant sources found, use direct generation
            response = await self.bedrock_client.generate_response(query)
            return response, [], 0.5
        
        # Build context from sources
        logger.info("Building context from retrieved sources...")
        context = self._build_context(sources)
        logger.info(f"Context built with {len(sources)} sources, length: {len(context)} characters")
        
        # Calculate confidence based on source relevance
        logger.info("Calculating confidence score...")
        confidence = self._calculate_confidence(sources)
        logger.info(f"Confidence calculated: {confidence:.3f}")
        
        # Generate response with context
        logger.info("Generating response with context...")
        response = await self._generate_with_context(query, context, sources)
        logger.info(f"Response generated, length: {len(response)} characters")
        
        return response, sources, confidence
    
    def _build_context(self, sources: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved sources"""
        logger.info(f"Building context from {len(sources)} sources...")
        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(f"{i}. {source['key_path']}: {source['content']}")
            logger.info(f"Added source {i}: {source['key_path']}")
        context = "\n".join(context_parts)
        logger.info(f"Context built successfully, {len(context_parts)} parts")
        return context
    
    def _calculate_confidence(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on source relevance"""
        if not sources:
            logger.warning("No sources provided for confidence calculation")
            return 0.0
        
        # Average distance (lower is better)
        distances = [source["distance"] for source in sources]
        avg_distance = sum(distances) / len(distances)
        logger.info(f"Average distance: {avg_distance:.4f} (distances: {[f'{d:.4f}' for d in distances]})")
        
        # Convert distance to confidence (0-1 scale)
        confidence = max(0.0, min(1.0, 1.0 - avg_distance / 2.0))
        logger.info(f"Calculated confidence: {confidence:.3f}")
        return confidence
    
    async def _generate_with_context(self, query: str, context: str, sources: List[Dict[str, Any]]) -> str:
        """Generate response using context and sources"""
        logger.info("Generating response with context and sources...")
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided knowledge base.

Knowledge Base Context:
{context}

User Question: {query}

Please answer the question based on the knowledge base context above. If the information is not available in the context, say so clearly. Be concise and accurate.

Answer:"""
        
        logger.info(f"Prompt prepared, length: {len(prompt)} characters")
        logger.info(f"Prompt preview: {prompt[:200]}...")
        
        response = await self.bedrock_client.generate_response(prompt)
        logger.info(f"Response received from Bedrock, length: {len(response)} characters")
        return response 