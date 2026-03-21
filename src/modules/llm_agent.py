"""
LLM Agent for Crop Recommendation System
=========================================================
This module integrates a local LLM (Llama3 via Ollama) to provide
farming advice, tips, and insights based on crop recommendations.

Uses HTTP requests to connect to the Ollama service running locally.

Author: ML Pipeline
Date: 2026
"""

import requests
from typing import Optional, List, Dict
from pathlib import Path


# ============================================================
# Configuration - Memory-Optimized Model Selection
# ============================================================

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Models prioritized by memory efficiency:
# - neural-chat: ~2.0 GiB (BEST for <4GB RAM)
# - phi: ~2.5 GiB (Good alternative)
# - mistral: ~4.0 GiB (if more RAM available)
# - llama3: ~4.6+ GiB (requires more memory)

MODELS_BY_MEMORY = [
    ("neural-chat", 2.0, "Best for 3-4 GB RAM"),
    ("phi", 2.5, "Good for 3-4 GB RAM"),
    ("mistral", 4.0, "Requires 4+ GB RAM"),
    ("llama3", 4.6, "Requires 5+ GB RAM")
]

# Use Phi for CPU-optimized inference (fastest on CPU without GPU)
# Phi-2.5: 2.7 GiB, ~10-15 tokens/sec on CPU, excellent for practical tasks
MODEL_NAME = "phi"


# ============================================================
# Model & Memory Detection Functions
# ============================================================

def get_available_models():
    """
    Fetch list of available models from Ollama.
    
    Returns:
        List[Dict]: List of available models or empty list if not accessible
    """
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("models", [])
    except:
        pass
    return []

def select_best_model():
    """
    Select the best available model based on system memory constraints.
    Falls back to progressively smaller models if needed.
    
    Returns:
        str: Model name to use
    """
    available = get_available_models()
    available_names = [m.get("name", "").split(":")[0] for m in available]
    
    # Try models in order of preference for low-memory systems
    for model_name, memory_gb, description in MODELS_BY_MEMORY:
        if any(model_name in name for name in available_names):
            return model_name
    
    # Fallback to first available model
    if available_names:
        return available_names[0].split(":")[0]
    
    # Default if nothing found
    return MODEL_NAME

# Detect best model on module load
try:
    MODEL_NAME = select_best_model()
except:
    pass  # Use default MODEL_NAME


# ============================================================
# Fallback Functions (When Ollama is not available)
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
    seed_varieties: Optional[List[Dict]] = None
) -> str:
    """
    Generate fallback agricultural advice without Ollama.
    Provides basic, pre-defined guidance based on crop and conditions.
    """
    
    # Basic crop-specific advice database
    crop_advice = {
        "rice": {
            "tips": [
                "Maintain consistent water level of 5-10 cm during growing period",
                "Apply nitrogen in splits: 50% at planting, 25% at tillering, 25% at panicle initiation",
                "Watch for pests like stem borers and leaf folders during mid-season"
            ],
            "challenge": "Waterlogging in low-lying areas during heavy rainfall"
        },
        "wheat": {
            "tips": [
                "Optimal sowing temperature: 20-25°C. Sow between October-November",
                "Apply 120 kg N/ha: 60 kg at sowing, 40 kg at CRI stage, 20 kg at heading",
                "Irrigation: First at CRI (25-30 days), second at booting stage (60-70 days)"
            ],
            "challenge": "Rust fungus can cause severe damage in warm, humid conditions"
        },
        "maize": {
            "tips": [
                "Spacing: 60 cm between rows, 25 cm between plants for better air circulation",
                "Apply K fertilizer before flowering for better grain development",
                "Irrigate when soil moisture reaches 50-60% depletion level"
            ],
            "challenge": "Fall armyworm and shoot fly infestations during growth stages"
        },
        "cotton": {
            "tips": [
                "Sow when minimum temperature is 20°C with adequate soil moisture",
                "Monitor for pink bollworm and jassids using pheromone traps",
                "Maintain phosphorus balance for better boll development"
            ],
            "challenge": "Bud and flower drop in extreme heat (>38°C)"
        },
        "sugarcane": {
            "tips": [
                "Spring planting (Feb-March) yields better than winter planting",
                "Apply 120-150 kg N/ha in splits at 45 and 100 days after planting",
                "Mulching helps conserve moisture and reduce weed growth"
            ],
            "challenge": "Red rot disease spreads rapidly in warm, humid conditions"
        }
    }
    
    crop_lower = crop.lower()
    advice_data = crop_advice.get(crop_lower, None)
    
    # Build the advice message
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
        advice += f"""\n**Farming Tips:**
"""
        for i, tip in enumerate(advice_data["tips"], 1):
            advice += f"{i}. {tip}\n"
        
        advice += f"""\n**Potential Challenge:**
⚠️ {advice_data["challenge"]}
"""
    else:
        advice += f"""\n**General Tips:**
1. Monitor soil moisture regularly and irrigate as needed
2. Follow the recommended nutrient schedule for {crop}
3. Scout fields regularly for pest and disease symptoms

**Potential Challenge:**
⚠️ Monitor for crop-specific diseases and pests based on local weather conditions
"""
    
    # Add seed variety information if available
    if seed_varieties and len(seed_varieties) > 0:
        advice += f"\n**Recommended Seed Varieties for {crop}:**\n"
        for i, seed in enumerate(seed_varieties, 1):
            advice += f"{i}. **{seed['Variety']}**\n"
            advice += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
            advice += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
            advice += f"   - Special Trait: {seed['Special_Trait']}\n"
    
    advice += "\n💡 **Note:** For more detailed AI-powered advice, please start the Ollama LLM service."
    
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
    seed_varieties: Optional[List[Dict]] = None
) -> Optional[str]:
    """
    Generate AI farming advice using Ollama Llama3 model.
    
    The function creates a detailed prompt based on the crop prediction
    and field conditions, then calls the local Ollama LLM to generate
    contextual farming advice. Optionally includes seed variety recommendations.
    
    Parameters:
    -----------
    crop : str
        Predicted crop name
    nitrogen : float
        Nitrogen content in kg/ha
    phosphorus : float
        Phosphorus content in kg/ha
    potassium : float
        Potassium content in kg/ha
    temperature : float
        Temperature in °C
    humidity : float
        Humidity percentage (0-100)
    ph : float
        Soil pH (3.5-10.0)
    rainfall : float
        Annual rainfall in mm
    season : str
        Farming season (Kharif/Rabi/Transition)
    seed_varieties : Optional[List[Dict]]
        List of recommended seed varieties with details
    
    Returns:
    --------
    str : AI-generated farming advice
    Optional[str] : None if API call fails
    """
    
    try:
        # Check if Ollama is available first
        if not is_ollama_available():
            # Fallback to template-based advice
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
                seed_varieties=seed_varieties
            )
        
        # Build seed variety information section if provided
        seed_info = ""
        if seed_varieties and len(seed_varieties) > 0:
            seed_info = "\n\nRecommended Seed Varieties:\n"
            for i, seed in enumerate(seed_varieties, 1):
                seed_info += f"{i}. {seed['Variety']} (Yield: {seed['Yield_t_ha']} t/ha, "
                seed_info += f"Disease Resistance: {seed['Disease_Resistance']}, "
                seed_info += f"Special Trait: {seed['Special_Trait']})\n"
        
        # Create prompt for the LLM
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

        # Prepare the API request - optimized for CPU inference
        # CPU-based systems: ~0.7s per token, so 80 tokens ≈ 20-30 sec response
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,  # Lower temp = faster generation on CPU
            "num_predict": 60     # Aggressive reduction for <20s response (CPU only!)
        }
        
        # Call the Ollama API with extended timeout
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            advice = result.get("response", "").strip()
            return advice
        elif response.status_code == 500:
            # Check for memory error
            response_text = response.text.lower()
            if "memory" in response_text or "out of memory" in response_text:
                print(f"⚠️  Memory warning: {response.text}")
            # Fallback to template-based advice on server error
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
                seed_varieties=seed_varieties
            )
        else:
            # If Ollama returns an error, fallback to template-based advice
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
                seed_varieties=seed_varieties
            )
    
    except requests.exceptions.ConnectionError:
        # Fallback to template-based advice if connection fails
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
            seed_varieties=seed_varieties
        )
    except requests.exceptions.Timeout:
        # Fallback to template-based advice on timeout
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
            seed_varieties=seed_varieties
        )
    except Exception as e:
        # Catch-all for any other error
        print(f"⚠️  LLM Error: {str(e)}")
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
            seed_varieties=seed_varieties
        )


def generate_seed_advice(
    crop: str,
    seed_varieties: List[Dict],
    region: str,
    season: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float
) -> Optional[str]:
    """
    Generate specialized AI advice for seed variety cultivation.
    
    Provides tailored guidance on why specific seed varieties were recommended
    and how to cultivate them optimally for the given conditions.
    
    Parameters:
    -----------
    crop : str
        Crop name
    seed_varieties : List[Dict]
        List of recommended seed varieties with details
    region : str
        User's geographic region
    season : str
        Farming season
    nitrogen : float
        Nitrogen content in kg/ha
    phosphorus : float
        Phosphorus content in kg/ha
    potassium : float
        Potassium content in kg/ha
    
    Returns:
    --------
    Optional[str] : Seed cultivation advice or None on error
    """
    
    try:
        # Check if Ollama is available
        if not is_ollama_available():
            # Return basic fallback seed advice
            advice = f"🌱 **Seed Variety Analysis for {crop}**\n\nSelected varieties suitable for {region} in {season}:\n\n"
            for i, seed in enumerate(seed_varieties, 1):
                advice += f"{i}. **{seed['Variety']}**\n"
                advice += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
                advice += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
                advice += f"   - Growing Duration: {seed['Duration_days']} days\n"
                advice += f"   - Special Trait: {seed['Special_Trait']}\n\n"
            advice += "💡 **Note:** For detailed cultivation advice, please start the Ollama LLM service."
            return advice
        
        # Build seed variety information
        seed_info = "Selected Seed Varieties:\n"
        for i, seed in enumerate(seed_varieties, 1):
            seed_info += f"\n{i}. {seed['Variety']}\n"
            seed_info += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
            seed_info += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
            seed_info += f"   - Growing Duration: {seed['Duration_days']} days\n"
            seed_info += f"   - Special Trait: {seed['Special_Trait']}\n"
        
        # Create detailed prompt for seed-specific advice
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

        # Prepare the API request - optimized for CPU inference
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,  # Lower temp = faster generation
            "num_predict": 100   # Reduced from 150 for speed
        }
        
        # Call the Ollama API
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            advice = result.get("response", "").strip()
            return advice
        else:
            # Fallback on error
            advice = f"🌱 **Seed Variety Analysis for {crop}**\n\nSelected varieties suitable for {region} in {season}:\n\n"
            for i, seed in enumerate(seed_varieties, 1):
                advice += f"{i}. **{seed['Variety']}**\n"
                advice += f"   - Expected Yield: {seed['Yield_t_ha']} t/ha\n"
                advice += f"   - Disease Resistance: {seed['Disease_Resistance']}\n"
                advice += f"   - Growing Duration: {seed['Duration_days']} days\n"
                advice += f"   - Special Trait: {seed['Special_Trait']}\n\n"
            return advice
    
    except Exception as e:
        # Return basic information on any error
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

def is_ollama_available() -> bool:
    """
    Check if Ollama service is running and accessible.
    
    Returns:
    --------
    bool : True if Ollama is available, False otherwise
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def generate_field_insights(
    seed_name: str,
    vegetation_level: str,
    vegetation_percentage: float,
    moisture_level: str,
    moisture_score: float,
    health_score: float,
    health_label: str
) -> str:
    """Generate AI field insights using LLM for personalized farming advice."""
    
    # Fallback for when LLM is unavailable
    def get_offline_advice():
        """Provides basic advice when LLM cannot be reached"""
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
        response += f"- Monitor field conditions regularly\n"
        response += f"- Apply preventive pest management\n"
        response += f"- Adjust irrigation based on moisture levels\n"
        return response
    
    # Try to get LLM analysis
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
        
        # Call LLM with sufficient timeout for response generation
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,  # Lower temp for faster CPU inference
                "num_predict": 100   # Reduced tokens for speed
            },
            timeout=300  # 5 minutes timeout
        )
        
        # Check if we got a good response
        if response.status_code == 200:
            result = response.json()
            insights = result.get("response", "").strip()
            
            # Return LLM response if substantial
            if insights and len(insights) > 100:
                return f"## 🤖 AI Field Analysis ({MODEL_NAME})\n\n{insights}"
        
        # Fall back if no good response
        return get_offline_advice()
    
    # Gracefully handle all errors
    except:
        return get_offline_advice()


def warm_up_model():
    """
    Warm up the LLM model by sending a quick test request.
    This loads the model into memory before the first real user request,
    preventing slow initial response times.
    """
    try:
        if not is_ollama_available():
            return False
        
        # Send a minimal prompt to load the model
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": "Hello",
                "stream": False,
                "temperature": 0.3,
                "num_predict": 10  # Very small response to keep it fast
            },
            timeout=120
        )
        
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    # Simple test script
    print("Testing LLM Agent...")
    
    if is_ollama_available():
        print("✓ Ollama service is available")
        
        # Test advice generation
        advice = generate_advice(
            crop="Rice",
            nitrogen=90,
            phosphorus=42,
            potassium=43,
            temperature=20.9,
            humidity=82.0,
            ph=6.5,
            rainfall=202.9,
            season="Kharif"
        )
        
        if advice:
            print("\n✓ Generated Advice:")
            print(advice)
        else:
            print("✗ Failed to generate advice")
    else:
        print("✗ Ollama service is not available. Make sure Ollama is running.")
