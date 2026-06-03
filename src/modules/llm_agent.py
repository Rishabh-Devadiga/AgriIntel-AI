"""
LLM Agent for Crop Recommendation System
========================================
This module formats agricultural prompts and routes them through the
Hugging Face-backed AgriLLM client used by the application.

Author: ML Pipeline
Date: 2026
"""

from typing import Dict, List, Optional

from agri_bot import (
    MODEL_ID as AGRI_MODEL_ID,
    ask_agriculture_expert,
    is_agriculture_expert_available,
)


# ============================================================
# Fallback Functions (When the HF model is not available)
# ============================================================

def get_fallback_advice(
    crop: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    season: str,
    seed_varieties: Optional[List[Dict]] = None,
) -> str:
    """Generate fallback agricultural advice without the remote model."""

    crop_advice = {
        "rice": {
            "tips": [
                "Maintain consistent water level of 5-10 cm during growing period",
                "Apply nitrogen in splits: 50% at planting, 25% at tillering, 25% at panicle initiation",
                "Watch for pests like stem borers and leaf folders during mid-season",
            ],
            "challenge": "Waterlogging in low-lying areas during heavy rainfall",
        },
        "wheat": {
            "tips": [
                "Optimal sowing temperature: 20-25°C. Sow between October-November",
                "Apply 120 kg N/ha: 60 kg at sowing, 40 kg at CRI stage, 20 kg at heading",
                "Irrigation: First at CRI (25-30 days), second at booting stage (60-70 days)",
            ],
            "challenge": "Rust fungus can cause severe damage in warm, humid conditions",
        },
        "maize": {
            "tips": [
                "Spacing: 60 cm between rows, 25 cm between plants for better air circulation",
                "Apply K fertilizer before flowering for better grain development",
                "Irrigate when soil moisture reaches 50-60% depletion level",
            ],
            "challenge": "Fall armyworm and shoot fly infestations during growth stages",
        },
        "cotton": {
            "tips": [
                "Sow when minimum temperature is 20°C with adequate soil moisture",
                "Monitor for pink bollworm and jassids using pheromone traps",
                "Maintain phosphorus balance for better boll development",
            ],
            "challenge": "Bud and flower drop in extreme heat (>38°C)",
        },
        "sugarcane": {
            "tips": [
                "Spring planting (Feb-March) yields better than winter planting",
                "Apply 120-150 kg N/ha in splits at 45 and 100 days after planting",
                "Mulching helps conserve moisture and reduce weed growth",
            ],
            "challenge": "Red rot disease spreads rapidly in warm, humid conditions",
        },
    }

    crop_lower = crop.lower()
    advice_data = crop_advice.get(crop_lower)

    advice = f"""🌾 **AI Crop Recommendation Analysis** 🌾

**Recommended Crop:** {crop}
**Season:** {season}

**Soil & Environmental Analysis:**
- Nitrogen Level: {nitrogen} kg/ha
- Phosphorus Level: {phosphorus} kg/ha
- Potassium Level: {potassium} kg/ha
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Soil pH: {ph}
- Annual Rainfall: {rainfall} mm

**Why {crop} is Suitable:**
The {crop} crop is well-suited for the current conditions with the available nutrients and climatic factors.
"""

    if advice_data:
        advice += "\n**Farming Tips:**\n"
        for i, tip in enumerate(advice_data["tips"], 1):
            advice += f"{i}. {tip}\n"

        advice += f"\n**Potential Challenge:**\n⚠️ {advice_data['challenge']}\n"
    else:
        advice += f"""\n**General Tips:**
1. Monitor soil moisture regularly and irrigate as needed
2. Follow the recommended nutrient schedule for {crop}
3. Scout fields regularly for pest and disease symptoms

**Potential Challenge:**
⚠️ Monitor for crop-specific diseases and pests based on local weather conditions
"""

    if seed_varieties and len(seed_varieties) > 0:
        advice += f"\n**Recommended Seed Varieties for {crop}:**\n"
        for i, seed in enumerate(seed_varieties, 1):
            advice += f"{i}. **{seed['Variety']}**\n"
            advice += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
            advice += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
            advice += f"   - Special Trait: {seed['Special_Trait']}\n"

    advice += "\n💡 **Note:** If AgriLLM is unavailable, configure the Hugging Face token to enable model-generated advice."
    return advice


# ============================================================
# LLM Functions for Crop Advice Generation
# ============================================================

def generate_advice(
    crop: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    season: str,
    seed_varieties: Optional[List[Dict]] = None,
) -> Optional[str]:
    """Generate AI farming advice using the Hugging Face-backed AgriLLM."""

    try:
        if not is_agriculture_expert_available():
            return get_fallback_advice(
                crop=crop,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                temperature=temperature,
                humidity=humidity,
                ph=ph,
                rainfall=rainfall,
                season=season,
                seed_varieties=seed_varieties,
            )

        seed_info = ""
        if seed_varieties and len(seed_varieties) > 0:
            seed_info = "\n\nRecommended Seed Varieties:\n"
            for i, seed in enumerate(seed_varieties, 1):
                seed_info += f"{i}. {seed['Variety']} (Yield: {seed['Yield_t_ha']} t/ha, "
                seed_info += f"Disease Resistance: {seed['Disease_Resistance']}, "
                seed_info += f"Special Trait: {seed['Special_Trait']})\n"

        prompt = f"""
You are an agricultural expert helping farmers.

Recommended crop: {crop}

Field conditions:
N: {nitrogen}
P: {phosphorus}
K: {potassium}
Temperature: {temperature} C
Humidity: {humidity} %
pH: {ph}
Rainfall: {rainfall} mm
Season: {season}
{seed_info}

Explain why this crop is suitable for these conditions.
If seed varieties are mentioned, explain why they were recommended.
Give 3 farming tips and 1 potential challenge.

Use short bullet points.
"""

        advice = ask_agriculture_expert(prompt).strip()
        if advice and not advice.startswith("AgriLLM "):
            return advice

        return get_fallback_advice(
            crop=crop,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            season=season,
            seed_varieties=seed_varieties,
        )

    except Exception:
        return get_fallback_advice(
            crop=crop,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            season=season,
            seed_varieties=seed_varieties,
        )


def generate_seed_advice(
    crop: str,
    seed_varieties: List[Dict],
    region: str,
    season: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
) -> Optional[str]:
    """Generate specialized AI advice for seed variety cultivation."""

    try:
        if not is_agriculture_expert_available():
            advice = f"🌱 **Seed Variety Analysis for {crop}**\n\nSelected varieties suitable for {region} in {season}:\n\n"
            for i, seed in enumerate(seed_varieties, 1):
                advice += f"{i}. **{seed['Variety']}**\n"
                advice += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
                advice += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
                advice += f"   - Growing Duration: {seed['Duration_days']} days\n"
                advice += f"   - Special Trait: {seed['Special_Trait']}\n\n"
            advice += "💡 **Note:** For detailed cultivation advice, configure the Hugging Face API token and reconnect AgriLLM."
            return advice

        seed_info = "Selected Seed Varieties:\n"
        for i, seed in enumerate(seed_varieties, 1):
            seed_info += f"\n{i}. {seed['Variety']}\n"
            seed_info += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
            seed_info += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
            seed_info += f"   - Growing Duration: {seed['Duration_days']} days\n"
            seed_info += f"   - Special Trait: {seed['Special_Trait']}\n"

        prompt = f"""
You are an expert agricultural consultant specializing in seed selection and cultivation.

Crop: {crop}
Region: {region}
Season: {season}

Soil Nutrients (kg/ha):
- Nitrogen: {nitrogen}
- Phosphorus: {phosphorus}
- Potassium: {potassium}

{seed_info}

For each recommended seed variety, provide:
1. Why this variety is suitable for the given conditions
2. Specific cultivation techniques for optimal yield
3. Pest and disease management specific to this variety
4. Typical challenges and how to overcome them
5. Expected harvest period

Keep the advice practical, concise, and farmer-friendly.
Use bullet points for clarity.
"""

        advice = ask_agriculture_expert(prompt).strip()
        if advice and not advice.startswith("AgriLLM "):
            return advice

        advice = f"🌱 **Seed Variety Analysis for {crop}**\n\nSelected varieties suitable for {region} in {season}:\n\n"
        for i, seed in enumerate(seed_varieties, 1):
            advice += f"{i}. **{seed['Variety']}**\n"
            advice += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
            advice += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
            advice += f"   - Growing Duration: {seed['Duration_days']} days\n"
            advice += f"   - Special Trait: {seed['Special_Trait']}\n\n"
        return advice

    except Exception:
        advice = f"🌱 **Seed Variety Analysis for {crop}**\n\nSelected varieties suitable for {region} in {season}:\n\n"
        for i, seed in enumerate(seed_varieties, 1):
            advice += f"{i}. **{seed['Variety']}**\n"
            advice += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
            advice += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
            advice += f"   - Growing Duration: {seed['Duration_days']} days\n"
            advice += f"   - Special Trait: {seed['Special_Trait']}\n\n"
        return advice


# ============================================================
# Utility Functions
# ============================================================

def is_agri_llm_available() -> bool:
    """Return whether the Hugging Face-backed AgriLLM is configured."""
    return is_agriculture_expert_available()


def get_model_id() -> str:
    """Return the configured Hugging Face model identifier."""
    return AGRI_MODEL_ID


def generate_field_insights(
    seed_name: str,
    vegetation_level: str,
    vegetation_percentage: float,
    moisture_level: str,
    moisture_score: float,
    health_score: float,
    health_label: str,
) -> str:
    """Generate AI field insights using the Hugging Face-backed AgriLLM."""

    def get_offline_advice():
        """Provides basic advice when the model cannot be reached."""
        risks = []
        if vegetation_percentage < 25:
            risks.append("🚨 **Critical vegetation shortage**: Possible disease, pest damage, or stress")
        elif vegetation_percentage < 50:
            risks.append("⚠️ **Below-target vegetation coverage**: Monitor closely")

        if moisture_score > 70:
            risks.append("💧 **High moisture detected**: Watch for waterlogging and fungal diseases")
        elif moisture_score < 30:
            risks.append("🏜️ **Low moisture detected**: Drought stress present - irrigation needed")

        if health_score < 6:
            risks.append("📊 **Field health below optimal**: Intervention recommended")

        response = "## 🤖 AI Field Analysis (Offline Mode)\n\n"
        response += "### ⚠️ **Potential Risks**\n"
        for risk in risks[:3]:
            response += f"- {risk}\n"
        response += f"\n### 🌾 **Cultivation Tips for {seed_name}**\n"
        response += "- Monitor field conditions regularly\n"
        response += "- Apply preventive pest management\n"
        response += "- Adjust irrigation based on moisture levels\n"
        return response

    try:
        prompt = f"""As an agricultural expert, analyze this specific field situation:

CROP: {seed_name}
VEGETATION COVERAGE: {vegetation_percentage}% ({vegetation_level})
SOIL MOISTURE: {moisture_score}% ({moisture_level})  
FIELD HEALTH SCORE: {health_score}/10

Based on THESE EXACT MEASUREMENTS, provide:

1. **POTENTIAL RISKS** - What specific problems exist with {vegetation_percentage}% vegetation and {moisture_score}% moisture?
2. **IMPROVEMENT ACTIONS** - What exact steps should the farmer take? (be specific with amounts/timing)
3. **TIPS FOR {seed_name}** - 3 specific practices for this crop variety given current conditions

Be practical, specific to the numbers provided, and actionable."""

        insights = ask_agriculture_expert(prompt).strip()
        if insights and not insights.startswith("AgriLLM ") and len(insights) > 100:
            return f"## 🤖 AI Field Analysis ({AGRI_MODEL_ID})\n\n{insights}"

        return get_offline_advice()

    except Exception:
        return get_offline_advice()


if __name__ == "__main__":
    print("Testing LLM Agent...")

    if is_agriculture_expert_available():
        print("✓ AgriLLM service is available")

        advice = generate_advice(
            crop="Rice",
            nitrogen=90,
            phosphorus=42,
            potassium=43,
            temperature=20.9,
            humidity=82.0,
            ph=6.5,
            rainfall=202.9,
            season="Kharif",
        )

        if advice:
            print("\n✓ Generated Advice:")
            print(advice)
        else:
            print("✗ Failed to generate advice")
    else:
        print("✗ AgriLLM service is not available. Check your Hugging Face token configuration.")
