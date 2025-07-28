import json
from typing import List, Dict, Any
import uuid

class DocumentProcessor:
    def __init__(self):
        self.chunks = []
    
    def process_json(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process JSON document into chunks by keys
        Each chunk contains the key path and its value
        """
        chunks = []
        self._process_json_recursive(json_data, "", chunks)
        return chunks
    
    def _process_json_recursive(self, data: Any, current_path: str, chunks: List[Dict[str, Any]]):
        """
        Recursively process JSON data and create chunks
        """
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key
                self._process_json_recursive(value, new_path, chunks)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{current_path}.{i}"
                self._process_json_recursive(item, new_path, chunks)
        
        else:
            # Leaf node - create chunk
            chunk = {
                "id": str(uuid.uuid4()),
                "key_path": current_path,
                "content": str(data),
                "metadata": {
                    "type": type(data).__name__,
                    "key_path": current_path
                }
            }
            chunks.append(chunk)
    
    def get_chunk_text(self, chunk: Dict[str, Any]) -> str:
        """
        Get formatted text representation of chunk for embedding
        """
        return f"{chunk['key_path']}: {chunk['content']}"
    
    def get_source_info(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get source information for attribution
        """
        return {
            "key_path": chunk["key_path"],
            "content": chunk["content"],
            "type": chunk["metadata"]["type"]
        } 