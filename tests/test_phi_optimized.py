#!/usr/bin/env python3
"""
Test Phi-2.5 response time with optimized parameters
"""
import requests
import time

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Test prompts of different complexities
prompts = {
    "Simple": ("What is 2+2?", 20),
    "Crop Recommendation": ("""You are an agricultural expert. Based on these soil conditions:
- Nitrogen: 50, Phosphorus: 30, Potassium: 40, pH: 6.5
Recommend a crop and give 2 tips.""", 80),
    "Field Analysis": ("""Analyze this field condition:
- Crop: Wheat, Vegetation: 65%, Moisture: 45%, Health Score: 7.2/10
Provide field assessment and irrigation recommendation.""", 100),
}

print("=" * 70)
print("PHI-2.5 RESPONSE TIMES (OPTIMIZED FOR CPU)")
print("=" * 70)

for test_name, (prompt, max_tokens) in prompts.items():
    try:
        print(f"\n[{test_name}] Max tokens: {max_tokens}")
        start = time.time()
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "phi",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
                "num_predict": max_tokens
            },
            timeout=180
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            resp_text = result.get("response", "")[:100].strip()
            print(f"  ⏱ Response time: {elapsed:.2f}s")
            print(f"  💬 Output: {resp_text}...")
        else:
            print(f"  ❌ ERROR: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

print("\n" + "=" * 70)
print("CPU-Based Inference Reality:")
print("  • Phi-2.5 on CPU: ~18-20 seconds per request (typical)")
print("  • Without GPU, sub-10 second responses aren't feasible")
print("  •→ SOLUTION: Use Phi + Offline Advice Fallback")
print("=" * 70)
