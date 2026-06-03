"""
Quick verification that field insights function works with fallback.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "src"))

from modules.llm_agent import generate_field_insights

# Test the fallback (no AgriLLM token needed)
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

print(insights.encode("ascii", "backslashreplace").decode("ascii"))
print("\nField insights function works!")
print("\nThis output will appear in the app even if AgriLLM is unavailable.")
