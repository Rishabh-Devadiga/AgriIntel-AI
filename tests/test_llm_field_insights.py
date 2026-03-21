"""
Test that LLM generates AI field advice (not offline mode)
"""
from llm_agent import generate_field_insights, is_ollama_available

print("=" * 70)
print("TESTING LLM FIELD INSIGHTS GENERATION")
print("=" * 70)

# Check LLM availability first
print(f"\n✓ Ollama Available: {is_ollama_available()}")

# Test field analysis
print("\n📋 Test Data:")
print("   Crop: Rice Var-25")
print("   Vegetation: 70% (Healthy)")
print("   Moisture: 48% (Medium)")
print("   Health Score: 6.2/10 (Moderate)")

print("\n🔄 Generating AI insights...\n")
print("-" * 70)

insights = generate_field_insights(
    seed_name="Rice Var-25",
    vegetation_level="Healthy",
    vegetation_percentage=70.0,
    moisture_level="Medium",
    moisture_score=48.0,
    health_score=6.2,
    health_label="Moderate"
)

print(insights)

print("-" * 70)

# Verify it's using LLM not offline
if "Offline Mode" in insights:
    print("\n❌ ISSUE: Still using offline mode")
    print("   Possible causes:")
    print("   1. Ollama not running")
    print("   2. neural-chat model not loaded")
    print("   3. Connection timeout")
    print("\n   Fix: Run check_llm_status.py for diagnostics")
elif "Neural-Chat LLM" in insights or "LLM" in insights:
    print("\n✅ SUCCESS: Using LLM for AI-powered advice!")
    print("   The LLM is analyzing your field data properly.")
else:
    print("\n✅ Response generated (may be LLM or offline)")
    if len(insights) > 300:
        print("   Length suggests LLM response (longer, more detailed)")
    else:
        print("   Length suggests offline response (shorter)")

print("=" * 70)
