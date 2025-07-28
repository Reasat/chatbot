#!/usr/bin/env python3
"""
Test script for the deployed chatbot system
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

def test_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    print("🔍 Testing frontend...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend check error: {e}")
        return False

def test_knowledge_base_upload():
    """Test knowledge base upload"""
    print("🔍 Testing knowledge base upload...")
    try:
        with open("sample_data.json", "rb") as f:
            files = {"file": ("sample_data.json", f, "application/json")}
            response = requests.post(f"{BACKEND_URL}/upload-knowledge-base", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge base uploaded successfully")
            print(f"   - Documents: {data['document_count']}")
            print(f"   - Chunks: {data['chunks_count']}")
            return True
        else:
            print(f"❌ Knowledge base upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Knowledge base upload error: {e}")
        return False

def test_chat_with_rag():
    """Test chat with RAG enabled"""
    print("🔍 Testing chat with RAG...")
    test_queries = [
        "What is the company name?",
        "How many employees does the company have?",
        "Who is the CEO?",
        "What are the products and their prices?"
    ]
    
    for query in test_queries:
        try:
            payload = {"message": query, "use_rag": True}
            response = requests.post(f"{BACKEND_URL}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query: '{query}'")
                print(f"   Response: {data['response'][:100]}...")
                print(f"   Sources: {len(data['sources'])} found")
                print(f"   Confidence: {data['confidence']:.2f}")
                print(f"   Processing time: {data['processing_time']:.4f}s")
            else:
                print(f"❌ Query failed: {query} - {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Query error: {query} - {e}")
            return False
    
    return True

def test_chat_without_rag():
    """Test chat without RAG"""
    print("🔍 Testing chat without RAG...")
    try:
        payload = {"message": "How many employees does the company have?", "use_rag": False}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Direct AI response: {data['response'][:100]}...")
            return True
        else:
            print(f"❌ Direct AI query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Direct AI query error: {e}")
        return False

def test_knowledge_base_status():
    """Test knowledge base status endpoint"""
    print("🔍 Testing knowledge base status...")
    try:
        response = requests.get(f"{BACKEND_URL}/knowledge-base-status")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge base status:")
            print(f"   - Loaded: {data['loaded']}")
            print(f"   - Documents: {data['document_count']}")
            print(f"   - Chunks: {data['chunks_count']}")
            return True
        else:
            print(f"❌ Knowledge base status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Knowledge base status error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Chatbot Deployment Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_health),
        ("Frontend Accessibility", test_frontend),
        ("Knowledge Base Upload", test_knowledge_base_upload),
        ("Knowledge Base Status", test_knowledge_base_status),
        ("Chat with RAG", test_chat_with_rag),
        ("Chat without RAG", test_chat_without_rag),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot is working correctly.")
        print("\n🌐 Access the application:")
        print(f"   Frontend: {FRONTEND_URL}")
        print(f"   Backend API: {BACKEND_URL}")
        print("\n📝 Next steps:")
        print("   1. Open the frontend URL in your browser")
        print("   2. Upload the sample_data.json file")
        print("   3. Start chatting with the AI!")
    else:
        print("❌ Some tests failed. Please check the deployment.")
    
    return passed == total

if __name__ == "__main__":
    main() 