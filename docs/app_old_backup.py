"""
AI Farm Intelligence System - Multi-Module Streamlit Application
================================================================
This application provides two integrated modules:

1. Crop Recommendation with Seed Intelligence
   - Uses ML model to predict best crop
   - Recommends seed varieties
   - Generates LLM-based cultivation advice

2. Field Intelligence
   - Analyzes field images for vegetation coverage
   - Estimates soil moisture using visual heuristics
   - Calculates field health score
   - Provides AI-powered field insights

Author: ML Pipeline
Date: 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import cv2
from pathlib import Path
from PIL import Image
import io
from llm_agent import generate_advice, is_ollama_available, generate_seed_advice
from seed_agent import get_seed_recommendations, SUPPORTED_REGIONS

# ============================================================
# Configuration
# ============================================================
st.set_page_config(
    page_title="AI Crop Recommendation System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Model and Data Loading
# ============================================================

@st.cache_resource
def load_model():
    """
    Load the trained Random Forest model from disk.
    Uses Streamlit cache to load the model only once.
    """
    try:
        model_path = "random_forest_crop_model.pkl"
        if not os.path.exists(model_path):
            st.error(f"❌ Model file not found: {model_path}")
            st.stop()
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        st.stop()


@st.cache_resource
def load_encoders():
    """
    Load the label encoders for categorical features.
    Uses Streamlit cache to load encoders only once.
    """
    try:
        encoders_path = "label_encoders.pkl"
        if not os.path.exists(encoders_path):
            st.warning("⚠️ Label encoders not found. Using default encoding.")
            return {}
        encoders = joblib.load(encoders_path)
        return encoders
    except Exception as e:
        st.warning(f"⚠️ Warning loading encoders: {str(e)}")
        return {}


@st.cache_resource
def load_feature_names():
    """
    Load feature names used during model training.
    Uses Streamlit cache to load feature names only once.
    """
    try:
        features_path = "feature_names.pkl"
        if not os.path.exists(features_path):
            return None
        features = joblib.load(features_path)
        
        # Handle case where features is loaded as a tuple (dtype, array)
        if isinstance(features, tuple) and len(features) > 1:
            features = features[1]  # Extract the array part
        
        # Convert to list if it's a numpy array
        if hasattr(features, 'tolist'):
            features = features.tolist()
        
        return features
    except Exception as e:
        return None


# ============================================================
# Prediction Function
# ============================================================

def predict_crop(model, encoders, feature_names, input_data):
    """
    Make a crop prediction using the trained model.
    
    Parameters:
    -----------
    model : RandomForestClassifier
        Trained model
    encoders : dict
        Dictionary of label encoders for categorical features
    feature_names : list
        Feature names used during training
    input_data : dict
        Input values from user
    
    Returns:
    --------
    str : Predicted crop name
    """
    try:
        # Create a dataframe from inputs in the correct order
        input_df = pd.DataFrame({
            'N': [input_data['nitrogen']],
            'P': [input_data['phosphorus']],
            'K': [input_data['potassium']],
            'temperature': [input_data['temperature']],
            'humidity': [input_data['humidity']],
            'ph': [input_data['ph']],
            'rainfall': [input_data['rainfall']],
            'Season': [input_data['season']]
        })
        
        # Encode the Season column if encoder is available
        if 'Season' in encoders:
            encoder = encoders['Season']
            input_df['Season'] = encoder.transform([input_data['season']])
        else:
            # Manual encoding fallback
            season_mapping = {'Kharif': 0, 'Rabi': 1, 'Transition': 2}
            input_df['Season'] = season_mapping.get(input_data['season'], 0)
        
        # Ensure columns are in the correct order
        if feature_names is not None:
            input_df = input_df[list(feature_names)]
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        
        return prediction
    
    except Exception as e:
        st.error(f"❌ Error during prediction: {str(e)}")
        return None


# ============================================================
# Field Intelligence Module - Image Analysis Functions
# ============================================================

def analyze_vegetation_coverage(image_array):
    """
    Analyze vegetation coverage by detecting green pixels.
    
    Parameters:
    -----------
    image_array : np.ndarray
        Image array in RGB format
    
    Returns:
    --------
    tuple : (vegetation_percentage, vegetation_level_label)
    """
    try:
        # Convert to HSV for better green detection
        hsv_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        
        # Define range for green color in HSV
        # Green hue range: 35-85 (approximately)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        
        # Create mask for green pixels
        green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
        
        # Calculate percentage of green pixels
        total_pixels = green_mask.size
        green_pixels = np.count_nonzero(green_mask)
        vegetation_percentage = (green_pixels / total_pixels) * 100
        
        # Classify vegetation level
        if vegetation_percentage > 50:
            level = "Healthy"
        elif vegetation_percentage > 25:
            level = "Moderate"
        else:
            level = "Low"
        
        return vegetation_percentage, level
    
    except Exception as e:
        st.error(f"❌ Error analyzing vegetation: {str(e)}")
        return 0, "Unknown"


def analyze_soil_moisture(image_array):
    """
    Estimate soil moisture using grayscale brightness analysis.
    
    Darker soil regions typically indicate higher moisture content.
    Lighter regions indicate drier soil.
    
    Parameters:
    -----------
    image_array : np.ndarray
        Image array in RGB format
    
    Returns:
    --------
    tuple : (moisture_score, moisture_level_label)
    """
    try:
        # Convert to grayscale
        gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Calculate average brightness (0-255 scale)
        avg_brightness = np.mean(gray_image)
        
        # Normalize to 0-100 scale (inverted: darker = more moisture)
        # Darker pixels (low brightness) = higher moisture
        # Lighter pixels (high brightness) = lower moisture
        moisture_score = 100 - (avg_brightness / 255 * 100)
        
        # Classify moisture level
        if moisture_score > 60:
            level = "High"
        elif moisture_score > 30:
            level = "Medium"
        else:
            level = "Low"
        
        return moisture_score, level
    
    except Exception as e:
        st.error(f"❌ Error analyzing moisture: {str(e)}")
        return 0, "Unknown"


def calculate_field_health_score(vegetation_percentage, moisture_score):
    """
    Calculate overall field health score.
    
    Formula: health_score = (vegetation_score * 0.6) + (moisture_score * 0.4)
    
    Parameters:
    -----------
    vegetation_percentage : float
        Vegetation coverage percentage (0-100)
    moisture_score : float
        Estimated moisture score (0-100)
    
    Returns:
    --------
    tuple : (health_score, health_label)
    """
    try:
        # Normalize vegetation to 0-10 scale
        vegetation_score = (vegetation_percentage / 10)
        
        # Normalize moisture to 0-10 scale
        moisture_normalized = (moisture_score / 10)
        
        # Calculate weighted health score
        health_score = (vegetation_score * 0.6) + (moisture_normalized * 0.4)
        
        # Classify health
        if health_score >= 7:
            label = "Healthy"
        elif health_score >= 4:
            label = "Moderate"
        else:
            label = "Poor"
        
        return round(health_score, 1), label
    
    except Exception as e:
        st.error(f"❌ Error calculating health score: {str(e)}")
        return 0, "Unknown"


def generate_field_insights(seed_name, vegetation_level, moisture_level, health_score):
    """
    Use LLM to generate AI field insights based on analysis.
    
    Parameters:
    -----------
    seed_name : str
        Name of seed/crop variety
    vegetation_level : str
        Vegetation level (Healthy/Moderate/Low)
    moisture_level : str
        Moisture level (High/Medium/Low)
    health_score : float
        Field health score (0-10)
    
    Returns:
    --------
    Optional[str] : AI-generated field insights
    """
    try:
        if not is_ollama_available():
            return None
        
        prompt = f"""
You are an agricultural expert analyzing field conditions.

Seed/Crop Variety: {seed_name}

Field Analysis Results:
- Vegetation Level: {vegetation_level}
- Soil Moisture Level: {moisture_level}
- Overall Field Health Score: {health_score}/10

Based on these field conditions, provide:

1. Potential Risks: What problems might arise with current conditions?
2. Improvement Suggestions: What actions should be taken?
3. Cultivation Tips: Specific advice for {seed_name}

Keep advice practical and farmer-friendly.
Use bullet points for clarity.
"""

        from llm_agent import OLLAMA_API_URL, MODEL_NAME
        import requests
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "num_predict": 300
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            insights = result.get("response", "").strip()
            return insights
        else:
            return None
    
    except Exception as e:
        return None


# ============================================================
# Page Functions for Sidebar Navigation
# ============================================================

def show_crop_recommendation_page(model, encoders, feature_names):
    """Display the Crop Recommendation with Seed Intelligence page."""
    """Main application function"""
    
    # Load model and encoders
    model = load_model()
    encoders = load_encoders()
    feature_names = load_feature_names()
    
    # ============================================================
    # Header Section
    # ============================================================
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🌾 AI Crop Recommendation System")
        st.markdown("""
        **Smart farming starts here!** This AI-powered system analyzes your field 
        conditions (soil nutrients, climate, and weather) to recommend the best 
        crop for maximum yield.
        """)
    
    with col2:
        st.image("https://via.placeholder.com/150?text=🌾", width=150)
    
    st.divider()
    
    # ============================================================
    # Sidebar - Information and Instructions
    # ============================================================
    with st.sidebar:
        st.header("📖 How to Use")
        
        # LLM Status Indicator
        if is_ollama_available():
            st.success("✅ LLM Ready - Ollama Connected")
        else:
            st.warning("⚠️ LLM Offline - Ollama Not Connected")
        
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Enter Soil Nutrients**
           - Nitrogen (N): in kg/ha
           - Phosphorus (P): in kg/ha
           - Potassium (K): in kg/ha
        
        2. **Enter Environmental Conditions**
           - Temperature: in °C
           - Humidity: in %
           - Soil pH: 0-14 scale
           - Rainfall: in mm
        
        3. **Select Season**
           - Choose from Kharif, Rabi, or Transition
        
        4. **Get Recommendation**
           - Click the button to receive your crop suggestion
        
        5. **AI Advice**
           - Get farming tips powered by Llama3 LLM
        
        ### About the System:
        - **Model**: Random Forest (100 trees)
        - **Accuracy**: 99.32% on test data
        - **LLM**: Llama3 (Local via Ollama)
        - **Data**: Based on Indian agricultural conditions
        - **22 Crops**: Covers major Indian crops
        """)
        
        st.divider()
        st.markdown("""
        ### Crop Types Covered:
        Rice, Wheat, Maize, Chickpea, Kidneybeans, 
        Pigeonpeas, Mothbeans, Mungbean, Blackgram, 
        Lentil, Pomegranate, Banana, Mango, Grapes, 
        Watermelon, Muskmelon, Apple, Orange, Papaya, 
        Coconut, Cotton, Jute, Coffee
        """)
        
        st.divider()
        
        if not is_ollama_available():
            st.markdown("""
            ### 🚀 Enable AI Advice
            
            **To get farming advice powered by AI:**
            
            1. Install Ollama from https://ollama.ai
            2. Open terminal and run:
               ```
               ollama pull llama3
               ollama serve
               ```
            3. Refresh this page
            
            The LLM will then generate personalized farming tips!
            """)
    
    # ============================================================
    # Main Input Section
    # ============================================================
    st.header("📋 Enter Your Field Conditions")
    
    # Create two columns for organized layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧪 Soil Nutrients (kg/ha)")
        nitrogen = st.slider(
            "Nitrogen (N)",
            min_value=0,
            max_value=150,
            value=50,
            step=5,
            help="Nitrogen content in soil (0-150 kg/ha)"
        )
        
        phosphorus = st.slider(
            "Phosphorus (P)",
            min_value=0,
            max_value=150,
            value=50,
            step=5,
            help="Phosphorus content in soil (0-150 kg/ha)"
        )
        
        potassium = st.slider(
            "Potassium (K)",
            min_value=0,
            max_value=210,
            value=50,
            step=5,
            help="Potassium content in soil (0-210 kg/ha)"
        )
    
    with col2:
        st.subheader("🌡️ Environmental Conditions")
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=50.0,
            value=25.0,
            step=0.5,
            help="Average temperature in °C"
        )
        
        humidity = st.slider(
            "Humidity",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=0.5,
            help="Relative humidity in %"
        )
        
        ph = st.slider(
            "Soil pH",
            min_value=3.5,
            max_value=10.0,
            value=6.5,
            step=0.1,
            help="Soil pH value (3.5-10.0)"
        )
        
        rainfall = st.slider(
            "Rainfall",
            min_value=0.0,
            max_value=300.0,
            value=100.0,
            step=5.0,
            help="Annual rainfall in mm"
        )
    
    st.divider()
    
    # Season and Location selection
    col1, col2 = st.columns(2)
    
    with col1:
        season = st.selectbox(
            "🌾 Select Season",
            options=["Kharif", "Rabi", "Transition"],
            index=0,
            help="Choose the farming season"
        )
    
    with col2:
        location = st.selectbox(
            "📍 Select Your Location",
            options=SUPPORTED_REGIONS,
            index=0,
            help="Select your region for seed recommendations"
        )
    
    st.divider()
    
    # ============================================================
    # Prediction Section
    # ============================================================
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        pred_button = st.button(
            "🎯 Get Crop Recommendation",
            use_container_width=True,
            type="primary"
        )
    
    if pred_button:
        # Prepare input data
        input_data = {
            'nitrogen': nitrogen,
            'phosphorus': phosphorus,
            'potassium': potassium,
            'temperature': temperature,
            'humidity': humidity,
            'ph': ph,
            'rainfall': rainfall,
            'season': season
        }
        
        # Make prediction
        predicted_crop = predict_crop(model, encoders, feature_names, input_data)
        
        if predicted_crop:
            # Store in session state for use in later sections
            st.session_state.predicted_crop = predicted_crop
            st.session_state.location = location
            
            # Get seed recommendations
            seed_recommendations = get_seed_recommendations(
                crop=predicted_crop.lower(),
                region=location,
                season=season,
                top_n=3
            )
            st.session_state.seed_recommendations = seed_recommendations
            
            # Display result
            st.divider()
            st.success("✅ Prediction Complete!")
            
            # Result box
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"""
                ### 🌿 Recommended Crop
                # **{predicted_crop.upper()}**
                """)
            
            # Display input summary
            st.subheader("📊 Your Field Conditions Summary")
            summary_df = pd.DataFrame({
                'Parameter': ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 
                             'Temperature', 'Humidity', 'Soil pH', 'Rainfall', 'Season', 'Location'],
                'Value': [f"{nitrogen} kg/ha", f"{phosphorus} kg/ha", f"{potassium} kg/ha",
                         f"{temperature}°C", f"{humidity}%", f"{ph}", f"{rainfall} mm", season, location]
            })
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # ============================================================
            # Seed Recommendations Section
            # ============================================================
            
            st.subheader("🌱 Recommended Seed Varieties")
            
            if seed_recommendations:
                st.success(f"✅ Found **{len(seed_recommendations)}** recommended seed varieties for {location}")
                
                # Display seed recommendations in columns
                for i, seed in enumerate(seed_recommendations):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        ### {i+1}. **{seed['Variety']}**
                        
                        - **Expected Yield**: {seed['Yield_t_ha']} t/ha
                        - **Disease Resistance**: {seed['Disease_Resistance']}
                        - **Growing Period**: {seed['Duration_days']} days
                        - **Special Trait**: {seed['Special_Trait']}
                        - **Best Season**: {seed['Season']}
                        """)
                    
                    with col2:
                        # Yield indicator
                        yield_percentage = min(100, (seed['Yield_t_ha'] / 40) * 100)
                        st.metric("Yield", f"{seed['Yield_t_ha']} t/ha")
                        
                st.divider()
            else:
                st.info(f"ℹ️ No specific seed varieties found for {predicted_crop} in {location}. "
                       "Using general recommendations based on crop type.")
            
            # ============================================================
            # LLM Integration - Generate AI Farming Advice
            # ============================================================
            
            st.subheader("🤖 AI Farming Advice")
            
            # Check if Ollama is available
            if not is_ollama_available():
                st.warning(
                    "⚠️ **Ollama LLM Service Not Available**\n\n"
                    "To get AI farming advice, please:\n"
                    "1. Install Ollama from https://ollama.ai\n"
                    "2. Run: `ollama pull llama3`\n"
                    "3. Start Ollama: `ollama serve`\n\n"
                    "Then refresh this page to enable AI advice generation."
                )
            else:
                # Create two tabs for different advice types
                tab1, tab2 = st.tabs(["📋 Crop & Field Advice", "🌱 Seed Cultivation Tips"])
                
                with tab1:
                    # Generate advice using LLM (with seed varieties)
                    with st.spinner("🔄 Generating AI farming advice using Llama3..."):
                        advice = generate_advice(
                            crop=predicted_crop,
                            nitrogen=nitrogen,
                            phosphorus=phosphorus,
                            potassium=potassium,
                            temperature=temperature,
                            humidity=humidity,
                            ph=ph,
                            rainfall=rainfall,
                            season=season,
                            seed_varieties=seed_recommendations if seed_recommendations else None
                        )
                    
                    if advice:
                        if advice.startswith("⚠️"):
                            st.warning(advice)
                        else:
                            st.success("✅ AI Advice Generated Successfully!")
                            st.markdown(advice)
                    else:
                        st.error("❌ Failed to generate AI advice. Please try again.")
                
                with tab2:
                    # Generate specialized seed advice if we have seed recommendations
                    if seed_recommendations and len(seed_recommendations) > 0:
                        with st.spinner("🔄 Generating seed cultivation advice using Llama3..."):
                            seed_advice = generate_seed_advice(
                                crop=predicted_crop,
                                seed_varieties=seed_recommendations,
                                region=location,
                                season=season,
                                nitrogen=nitrogen,
                                phosphorus=phosphorus,
                                potassium=potassium
                            )
                        
                        if seed_advice:
                            st.success("✅ Seed Cultivation Advice Generated!")
                            st.markdown(seed_advice)
                        else:
                            st.info("ℹ️ Specialized seed advice is currently unavailable.")
                    else:
                        st.info("ℹ️ Seed cultivation advice will be displayed once seed varieties are identified.")
    
    # ============================================================
    # Future LLM Features - Roadmap
    # ============================================================
    
    st.divider()
    st.subheader("🚀 Future LLM Features")
    st.markdown("""
    The following AI-powered features are under development:
    
    - **🦠 Crop Disease Detection**: Identify potential diseases based on field conditions
    - **🧪 Fertilizer Optimization**: Get personalized fertilizer recommendations
    - **🌤️ Weather-Based Farming**: Receive season-specific farming advice
    - **💬 Farmer Chatbot**: Interactive Q&A for agricultural guidance
    - **📊 Crop Analytics**: Market analysis and pricing trends
    - **🎯 Yield Prediction**: Estimate expected crop yield
    - **🔄 Crop Rotation Planning**: Plan multi-season cropping strategies
    
    All features powered by **Llama3 LLM** running locally via Ollama.
    """)
    
    # ============================================================
    # Footer
    # ============================================================
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col2:
        st.caption("🌍 AI Crop Recommendation System | Powered by Random Forest ML Model")
        st.caption("© 2026 Agricultural AI Solutions | Built with Streamlit")


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":
    main()
