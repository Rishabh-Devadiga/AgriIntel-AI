#!/usr/bin/env python3
"""
Test Mistral response time directly
"""
import requests
import time

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def test_mistral_response_time():
    """Test the actual response time from Mistral"""
    
    try:
        print("Testing Mistral response time...")
        print("=" * 60)
        
        # Test 1: Simple short prompt
        print("\n[TEST 1] Simple prompt (10 tokens max)")
        start = time.time()
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "mistral",
                "prompt": "What is 2+2?",
                "stream": False,
                "temperature": 0.5,
                "num_predict": 10
            },
            timeout=120
        )
        elapsed = time.time() - start
        print(f"Response time: {elapsed:.2f} seconds")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', '')[:100]}...")
        else:
            print(f"ERROR: {response.status_code}")
        
        # Test 2: Medium prompt (120 tokens - same as generate_advice)
        print("\n[TEST 2] Medium prompt (120 tokens max)")
        prompt = """You are an agricultural expert. Based on these soil conditions:
- Nitrogen: 50
- Phosphorus: 30
- Potassium: 40
- pH: 6.5

Recommend a crop and provide 2 farming tips."""
        
        start = time.time()
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.5,
                "num_predict": 120
            },
            timeout=120
        )
        elapsed = time.time() - start
        print(f"Response time: {elapsed:.2f} seconds")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', '')[:150]}...")
        else:
            print(f"ERROR: {response.status_code}")
        
        # Test 3: Larger prompt (150 tokens - same as generate_field_insights)
        print("\n[TEST 3] Larger prompt (150 tokens max)")
        prompt = """Analyze this field condition:
- Crop: Wheat
- Vegetation: 65%
- Moisture: 45%
- Health Score: 7.2/10

Provide:
1. Field health assessment
2. Irrigation recommendation
3. Disease prevention tips"""
        
        start = time.time()
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.5,
                "num_predict": 150
            },
            timeout=120
        )
        elapsed = time.time() - start
        print(f"Response time: {elapsed:.2f} seconds")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', '')[:150]}...")
        else:
            print(f"ERROR: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("Test complete. If times are >15 seconds, there's a performance issue.")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_mistral_response_time()
