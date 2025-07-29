#!/usr/bin/env python3
"""
Quick verification script for the minimal AWS chatbot
"""

import sys
import os

# Add backend to path
sys.path.append('backend')

def verify_setup():
    """Verify the setup is working"""
    print("🔍 Verifying Minimal AWS Chatbot Setup...")
    
    # Test imports
    try:
        from rag.document_processor import DocumentProcessor
        from rag.vector_store import VectorStore
        from rag.retrieval import RAGPipeline
        from aws.bedrock_client import BedrockClient
        from aws.embedding_client import AWSBedrockEmbeddings
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test class instantiation
    try:
        doc_processor = DocumentProcessor()
        vector_store = VectorStore(mock_mode=True)
        bedrock_client = BedrockClient(mock_mode=True)
        rag_pipeline = RAGPipeline(vector_store, bedrock_client)
        embedding_client = AWSBedrockEmbeddings(mock_mode=True)
        print("✅ All classes instantiated successfully")
    except Exception as e:
        print(f"❌ Class instantiation failed: {e}")
        return False
    
    # Test basic functionality
    try:
        # Test embedding
        embedding = embedding_client.embed_text("test")
        print(f"✅ Embedding generation: {len(embedding)} dimensions")
        
        # Test document processing
        test_data = {"test": "data"}
        chunks = doc_processor.process_json(test_data)
        print(f"✅ Document processing: {len(chunks)} chunks")
        
        # Test vector store
        vector_store.add_documents(chunks)
        results = vector_store.search("test", top_k=1)
        print(f"✅ Vector store operations: {len(results)} results")
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False
    
    print("\n🎉 Setup verification successful!")
    print("\n📋 Next steps:")
    print("1. Configure AWS credentials: cp backend/env.example backend/.env")
    print("2. Start the application: bash run.sh")
    print("3. Open frontend: cd frontend && python -m http.server 8080")
    
    return True

if __name__ == "__main__":
    success = verify_setup()
    if not success:
        print("\n❌ Setup verification failed. Check the error messages above.")
        exit(1) 