"""
Test script for the RAG API
Tests the /ask endpoint with sample questions
"""

import requests
import json
import time

# Wait a moment for server to start
time.sleep(2)

API_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("TESTING RAG API")
print("=" * 70)

# Test 1: Health check
print("\n1️⃣  Testing /health endpoint...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Ask about refund policy
print("\n2️⃣  Testing /ask endpoint - Refund question...")
try:
    question_data = {"question": "What is the refund policy?"}
    response = requests.post(f"{API_URL}/ask", json=question_data, timeout=10)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    print(f"Chunks used: {result['num_chunks_used']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Ask about shipping
print("\n3️⃣  Testing /ask endpoint - Shipping question...")
try:
    question_data = {"question": "How long does shipping take?"}
    response = requests.post(f"{API_URL}/ask", json=question_data, timeout=10)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Ask about warranty
print("\n4️⃣  Testing /ask endpoint - Warranty question...")
try:
    question_data = {"question": "How long is the warranty?"}
    response = requests.post(f"{API_URL}/ask", json=question_data, timeout=10)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Ask something not in documents
print("\n5️⃣  Testing /ask endpoint - Question not in documents...")
try:
    question_data = {"question": "What is your return address?"}
    response = requests.post(f"{API_URL}/ask", json=question_data, timeout=10)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE!")
print("=" * 70)
print("\n💡 TIP: Visit http://127.0.0.1:8000/docs for interactive API documentation")
