"""
Quick verification that field insights function works with fallback
"""
from llm_agent import generate_field_insights

# Test the fallback (no Ollama needed)
print("Testing generate_field_insights with fallback mode...\n")

insights = generate_field_insights(
    seed_name="Rice Var-25",
    vegetation_level="Healthy",
    vegetation_percentage=70,
    moisture_level="Medium",
    moisture_score=48,
    health_score=6.2,
    health_label="Moderate"
)

print(insights)
print("\n✅ Field insights function works!")
print("\nThis output will appear in the app even if Ollama is offline.")
