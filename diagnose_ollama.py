"""
Ollama Diagnostic Script
Helps troubleshoot LLM service issues (500 errors, connection failures, etc.)
"""

import requests
import sys
from time import sleep

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
MODEL_NAME = "llama3"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_ollama_running():
    """Check if Ollama service is running"""
    print_section("1. Checking Ollama Service Connection")
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is RUNNING")
            return True
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at " + OLLAMA_API_URL)
        print("   Make sure to run: ollama serve")
        return False
    except requests.exceptions.Timeout:
        print("❌ Ollama connection timeout")
        return False

def list_available_models():
    """List all available models in Ollama"""
    print_section("2. Available Models")
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            if models:
                print(f"Found {len(models)} model(s):\n")
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3)
                    print(f"  • {name} ({size_gb:.1f} GB)")
                    
                # Check if llama3 is available
                model_names = [m.get("name", "") for m in models]
                if any("llama3" in name for name in model_names):
                    print(f"\n✅ llama3 is available")
                    return True
                else:
                    print(f"\n❌ llama3 NOT found")
                    print("   Run: ollama pull llama3")
                    return False
            else:
                print("❌ No models found")
                print("   Run: ollama pull llama3")
                return False
        else:
            print(f"FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_basic_generation():
    """Test Ollama with a simple generation request"""
    print_section("3. Testing Basic Generation")
    
    prompt = "What is 2+2? Answer in one word."
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.5,
        "num_predict": 10
    }
    
    print("Sending test prompt...")
    print(f"Prompt: '{prompt}'")
    print(f"Model: {MODEL_NAME}\n")
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()
            print(f"✅ Generation successful!")
            print(f"Response: '{response_text}'")
            print(f"Status Code: {response.status_code}")
            return True
        
        elif response.status_code == 500:
            print(f"❌ SERVER ERROR (Status: 500)")
            print(f"Response body:\n{response.text}")
            print("\n💡 Common causes:")
            print("   • Ollama out of memory (try restarting)")
            print("   • Model crashed (try: ollama pull llama3 again)")
            print("   • Ollama service unstable (try: kill ollama and run: ollama serve)")
            return False
        
        else:
            print(f"❌ Error (Status: {response.status_code})")
            print(f"Response:\n{response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timeout (LLM took too long)")
        print("   The model might be loading or overloaded")
        return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused")
        print("   Ollama service is not running")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_field_intelligence_prompt():
    """Test with actual field intelligence prompt"""
    print_section("4. Testing Field Intelligence Prompt")
    
    prompt = """
You are an agricultural expert analyzing field conditions.

Seed/Crop Variety: Rice Var-25

Field Analysis Results:
- Vegetation Level: Healthy (70% coverage)
- Soil Moisture Level: Medium (48% estimated)
- Overall Field Health Score: 6.2/10 (Moderate)

Based on these conditions, provide:

1. **Potential Risks**: What problems might arise?
2. **Improvement Suggestions**: What actions should be taken?
3. **Cultivation Tips**: Specific advice for Rice Var-25

Keep advice practical and farmer-friendly. Use bullet points.
""".strip()
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.7,
        "num_predict": 300
    }
    
    print("Sending field intelligence test prompt...")
    print(f"Model: {MODEL_NAME}\n")
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()
            print(f"✅ Field Intelligence Generation successful!")
            print(f"\nResponse preview (first 500 chars):")
            print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            print(f"\nStatus Code: {response.status_code}")
            return True
        
        elif response.status_code == 500:
            print(f"❌ SERVER ERROR (Status: 500)")
            print(f"Response:\n{response.text[:1000]}")
            return False
        
        else:
            print(f"❌ Error (Status: {response.status_code})")
            print(f"Response:\n{response.text[:500]}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_recommendations():
    """Show troubleshooting recommendations"""
    print_section("5. Troubleshooting Recommendations")
    
    print("""
🔧 IF OLLAMA IS NOT RUNNING:
   1. Open PowerShell / Command Prompt
   2. Run: ollama serve
   3. Wait for startup (~5 seconds)
   4. Try the app again

🔧 IF YOU GET 500 ERROR:
   1. Restart Ollama:
      - Stop current process (Ctrl+C)
      - Wait 2 seconds
      - Run: ollama serve
   
   2. Reload the model:
      - In new PowerShell: ollama pull llama3
      - This may take time if model needs download
   
   3. Check available memory:
      - Llama3 needs 4-8 GB RAM
      - Close other apps if needed
   
   4. Check Ollama logs for errors

🔧 IF CONNECTION FAILS:
   - Verify Ollama is running: ollama serve
   - Check port 11434 is not blocked
   - Try: curl http://localhost:11434/api/tags

📚 USEFUL COMMANDS:
   ollama list          → Show all models
   ollama pull llama3   → Download/update llama3
   ollama serve         → Start Ollama service
   ollama ps            → Show running models
""")

def main():
    print("\n" + "="*60)
    print("  OLLAMA DIAGNOSTIC TOOL v1.0")
    print("="*60)
    
    # Run diagnostics
    ollama_running = check_ollama_running()
    
    if not ollama_running:
        print("\n🛑 Cannot proceed without Ollama running")
        show_recommendations()
        return 1
    
    models_available = list_available_models()
    basic_test = test_basic_generation()
    field_test = test_field_intelligence_prompt()
    
    # Summary
    print_section("DIAGNOSTIC SUMMARY")
    
    print("✅ Ollama Service: RUNNING")
    print(f"{'✅' if models_available else '❌'} Models: {'Available' if models_available else 'NOT AVAILABLE'}")
    print(f"{'✅' if basic_test else '❌'} Basic Generation: {'WORKING' if basic_test else 'FAILED'}")
    print(f"{'✅' if field_test else '❌'} Field Intelligence: {'WORKING' if field_test else 'FAILED'}")
    
    if field_test:
        print("\n🎉 All tests passed! Your Ollama is ready for the app.")
        return 0
    else:
        print("\n⚠️  Some tests failed. See recommendations above.")
        show_recommendations()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostic interrupted by user")
        sys.exit(1)
