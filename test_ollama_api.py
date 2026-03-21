"""
Direct API test to Ollama - no wrapper functions
"""
import requests
import json

print("=" * 70)
print("DIRECT OLLAMA API TEST")
print("=" * 70)

url = "http://localhost:11434/api/generate"
payload = {
    "model": "neural-chat",
    "prompt": "Analyze this field: 70% vegetation (healthy), 48% moisture (medium). What are the risks? Keep response under 100 words.",
    "stream": False,
    "temperature": 0.3,
    "num_predict": 100
}

print("\nSending request to:", url)
print("Model: neural-chat")
print("Prompt: Field analysis request")

try:
    response = requests.post(url, json=payload, timeout=120)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        response_text = result.get("response", "").strip()
        print(f"Response Length: {len(response_text)} chars")
        print(f"\nResponse:\n{response_text}")
        
        if len(response_text) > 30:
            print("\n✅ LLM IS WORKING - Direct API works!")
        else:
            print("\n⚠️ Empty response from LLM")
    else:
        print(f"Error Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
except requests.exceptions.Timeout:
    print("❌ Request timed out (120s)")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
