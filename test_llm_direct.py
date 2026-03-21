"""
Direct test of LLM field insights - shows exactly what's happening
"""
import sys
from llm_agent import generate_field_insights, is_ollama_available, MODEL_NAME, OLLAMA_API_URL
import requests

print("=" * 70)
print("DIRECT LLM FIELD INSIGHTS TEST")
print("=" * 70)

# Step 1: Verify Ollama
print("\n[STEP 1] Checking Ollama connection...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"✅ Ollama RUNNING - {len(models)} models available")
        for m in models:
            print(f"   • {m.get('name')}")
    else:
        print(f"❌ Ollama status code: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect: {e}")
    sys.exit(1)

# Step 2: Check configured model
print(f"\n[STEP 2] Configured model: {MODEL_NAME}")
print(f"         API endpoint: {OLLAMA_API_URL}")

# Step 3: Call generate_field_insights
print("\n[STEP 3] Calling generate_field_insights with test data...")
print("         Seed: RiceVar25")
print("         Vegetation: 70% (Healthy)")
print("         Moisture: 48% (Medium)")
print("         Health: 6.2/10 (Moderate)")
print("\n" + "-" * 70)

result = generate_field_insights(
    seed_name="RiceVar25",
    vegetation_level="Healthy",
    vegetation_percentage=70.0,
    moisture_level="Medium",
    moisture_score=48.0,
    health_score=6.2,
    health_label="Moderate"
)

print(result)
print("-" * 70)

# Step 4: Analyze result
print("\n[STEP 4] Analyzing result...")

if "Offline Mode" in result:
    print("❌ OFFLINE MODE - LLM was not used!")
    print("\n   Possible reasons:")
    print("   1. Ollama not actually responding to generate calls")
    print("   2. Model returned empty")
    print("   3. Timeout occurred")
    print("\n   Try: Restart Ollama, then reload app")
else:
    print(f"✅ LLM RESPONSE DETECTED")
    lines = result.split('\n')
    print(f"   Response has {len(lines)} lines")
    print(f"   Response length: {len(result)} characters")
    
    # Check content quality
    if "Potential Risks" in result or "RISKS" in result:
        print("   ✓ Contains Risk analysis")
    if "Improvement" in result or "Suggestions" in result or "ACTIONS" in result:
        print("   ✓ Contains Improvement suggestions")
    if "Cultivation" in result or "TIPS" in result:
        print("   ✓ Contains Cultivation tips")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
