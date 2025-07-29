import boto3
import json
from typing import List, Optional
import os

class AWSBedrockEmbeddings:
    def __init__(self, model_id: str = "amazon.titan-embed-text-v1", mock_mode: bool = False):
        self.model_id = model_id
        self.mock_mode = mock_mode
        
        if not mock_mode:
            # Initialize Bedrock client for embeddings
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for a single text using AWS Titan
        """
        if self.mock_mode:
            return self._generate_mock_embedding(text)
        
        try:
            # Prepare request body for Titan embeddings
            request_body = {
                "inputText": text
            }
            
            # Make API call
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body['embedding']
            
            return embedding
            
        except Exception as e:
            print(f"Error calling AWS Bedrock for embeddings: {str(e)}")
            # Return mock embedding as fallback
            return self._generate_mock_embedding(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)
        """
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Generate mock embeddings for testing without AWS
        Returns a 1536-dimensional vector (same as Titan)
        """
        import hashlib
        import random
        
        # Use text hash as seed for consistent mock embeddings
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        random.seed(seed)
        
        # Generate 1536-dimensional mock embedding
        embedding = [random.uniform(-1, 1) for _ in range(1536)]
        
        # Normalize the embedding
        magnitude = sum(x * x for x in embedding) ** 0.5
        normalized_embedding = [x / magnitude for x in embedding]
        
        return normalized_embedding
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        """
        return 1536  # Titan embedding dimension 