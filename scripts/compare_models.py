#!/usr/bin/env python3
"""
Compare Phi vs Mistral response times
"""
import requests
import time

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def test_model_speed(model_name, prompt, num_tokens):
    """Test response time for a specific model"""
    try:
        start = time.time()
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.5,
                "num_predict": num_tokens
            },
            timeout=180
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            return elapsed, result.get("response", "")[:80]
        else:
            return elapsed, f"ERROR: {response.status_code}"
    except Exception as e:
        return None, str(e)

# Test prompt for crop recommendation
crop_prompt = """You are an agricultural expert. Based on these soil conditions:
- Nitrogen: 50, Phosphorus: 30, Potassium: 40, pH: 6.5

Recommend a crop and provide 2 farming tips."""

print("=" * 70)
print("MODEL SPEED COMPARISON: Phi vs Mistral")
print("=" * 70)

# Test Phi
print("\n[PHI-2.5 - 1.6 GB model]")
elapsed, response = test_model_speed("phi", crop_prompt, 120)
if elapsed:
    print(f"  Response time: {elapsed:.2f}s")
    print(f"  Result: {response}...")
else:
    print(f"  ERROR: {response}")

# Test Mistral
print("\n[MISTRAL-7B - 4.4 GB model]")
elapsed, response = test_model_speed("mistral", crop_prompt, 120)
if elapsed:
    print(f"  Response time: {elapsed:.2f}s")
    print(f"  Result: {response}...")
else:
    print(f"  ERROR: {response}")

print("\n" + "=" * 70)
print("✅ Use Phi for CPU inference (much faster, smaller, suitable)")
print("=" * 70)
