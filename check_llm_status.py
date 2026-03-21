"""
Quick diagnostic to check LLM status
"""
import requests

print("=" * 60)
print("LLM CONNECTIVITY CHECK")
print("=" * 60)

# Check if Ollama is running
print("\n1️⃣  Checking if Ollama is running...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        print("✅ Ollama is RUNNING!")
        
        # Check what models are available
        data = response.json()
        models = data.get("models", [])
        
        if models:
            print(f"\n2️⃣  Available models ({len(models)}):")
            for model in models:
                name = model.get("name", "Unknown")
                print(f"   • {name}")
        else:
            print("\n❌ No models found!")
            print("   Need to download a model:")
            print("   → ollama pull neural-chat")
    else:
        print(f"❌ Ollama not responding properly (Status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("❌ OLLAMA NOT RUNNING")
    print("\n   💡 To fix:")
    print("   1. Open PowerShell")
    print("   2. Run: ollama serve")
    print("   3. Keep it running in background")
    print("   4. Reload the Streamlit app")
except requests.exceptions.Timeout:
    print("❌ Ollama timeout (may be starting up)")

# Test what the app is using
print("\n" + "=" * 60)
print("APP CONFIGURATION")
print("=" * 60)

from llm_agent import MODEL_NAME, is_ollama_available

print(f"\nConfigured Model: {MODEL_NAME}")
print(f"LLM Available: {is_ollama_available()}")

if not is_ollama_available():
    print("\n⚠️  The app will use OFFLINE MODE for insights")
    print("    (Still shows useful farming advice, just not AI-generated)")
else:
    print("\n✅ The app will use LLM for AI-powered insights")

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)

if not is_ollama_available():
    print("""
To enable AI-powered Field Insights:

Option 1: Pull neural-chat (RECOMMENDED - 2.0 GB)
   ollama pull neural-chat

Option 2: Pull phi (alternative - 2.5 GB)
   ollama pull phi

Then restart Ollama:
   killall ollama  (if running)
   ollama serve    (restart)

Then reload your Streamlit app.
""")
else:
    print("\n✅ Your LLM is ready! AI Field Insights should work.")
    print("   If still seeing offline mode, restart the Streamlit app.")

print("=" * 60)
