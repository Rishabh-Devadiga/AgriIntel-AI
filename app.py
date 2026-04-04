"""
AI Farm Intelligence System - Multi-Module Streamlit Application
================================================================
A comprehensive agricultural AI system with two integrated modules:

1. Crop Recommendation with Seed Intelligence
   - ML-based crop prediction
   - Seed variety recommendations
   - LLM-powered cultivation advice

2. Field Intelligence 
   - Image-based field analysis
   - Vegetation coverage estimation
   - Soil moisture assessment
   - Field health scoring
   - AI field insights

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
from typing import Optional
import sys

# Add src to path for module imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import custom modules from src/modules
from modules.llm_agent import generate_advice, is_ollama_available, generate_seed_advice, generate_field_insights, warm_up_model, OLLAMA_API_URL, MODEL_NAME
from modules.seed_agent import get_seed_recommendations, SUPPORTED_REGIONS
from modules.field_intelligence import (
    analyze_vegetation_coverage,
    analyze_soil_moisture,
    calculate_field_health_score,
    generate_field_report
)

import requests


# ============================================================
# Configuration & Page Setup
# ============================================================

st.set_page_config(
    page_title="AI Farm Intelligence System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# Session State & Model Warm-up for Performance
# ============================================================

# Initialize session state for warm-up tracking
if "model_warmed_up" not in st.session_state:
    st.session_state.model_warmed_up = False

# Warm up the LLM model on first app load (prevents slow first response)
if not st.session_state.model_warmed_up and is_ollama_available():
    try:
        with st.spinner("🔄 Loading AI model..."):
            if warm_up_model():
                st.session_state.model_warmed_up = True
    except:
        pass  # Warm-up failed, but app continues


# ============================================================
# Model Loading Functions (Cached)
# ============================================================

@st.cache_resource
def load_model():
    """Load the trained Random Forest model from models/ directory."""
    try:
        model_path = Path(__file__).parent / "models" / "random_forest_crop_model.pkl"
        if not os.path.exists(model_path):
            st.error(f"❌ Model file not found: {model_path}")
            st.stop()
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        st.stop()


@st.cache_resource
def load_encoders():
    """Load the label encoders for categorical features from models/ directory."""
    try:
        encoders_path = Path(__file__).parent / "models" / "label_encoders.pkl"
        if not os.path.exists(encoders_path):
            return {}
        return joblib.load(encoders_path)
    except Exception as e:
        return {}


@st.cache_resource
def load_feature_names():
    """Load feature names used during model training from models/ directory."""
    try:
        features_path = Path(__file__).parent / "models" / "feature_names.pkl"
        if not os.path.exists(features_path):
            return None
        features = joblib.load(features_path)
        
        # Handle case where features is loaded as a tuple
        if isinstance(features, tuple) and len(features) > 1:
            features = features[1]
        
        if hasattr(features, 'tolist'):
            features = features.tolist()
        
        return features
    except Exception as e:
        return None


# ============================================================
# LLM Query Function for AI Insights Panel
# ============================================================

def ask_ai_insight(
    question: str,
    health_score: Optional[float] = None,
    vegetation_level: Optional[str] = None,
    seed_name: Optional[str] = None
) -> str:
    """
    Query the local LLM model via Ollama API to get agricultural insights.
    
    Optimized prompt design ensures:
    - Focused, agriculture-only responses
    - No hallucinations or off-topic content
    - Concise answers (max 80 words)
    - Practical farmer-friendly advice
    
    Parameters:
    -----------
    question : str
        The user's farming question
    health_score : Optional[float]
        Field health score (0-10) if available
    vegetation_level : Optional[str]
        Vegetation level description if available
    seed_name : Optional[str]
        Selected seed/crop variety if available
    
    Returns:
    --------
    str : Focused agricultural advice
    """
    try:
        # Build context section if available
        context = ""
        if health_score is not None or vegetation_level or seed_name:
            context = "\nCurrent Field Information:\n"
            if health_score is not None:
                context += f"- Field Health Score: {health_score}/10\n"
            if vegetation_level:
                context += f"- Vegetation Level: {vegetation_level}\n"
            if seed_name:
                context += f"- Seed/Crop Selected: {seed_name}\n"
        
        # Structured prompt with clear rules and constraints
        prompt = f"""You are an agricultural advisor helping farmers with practical advice.

Rules:
• Answer ONLY questions related to farming, crops, soil, fertilizers, irrigation, and field conditions.
• Do NOT generate stories, riddles, examples beyond what's asked, or unrelated content.
• Use simple language that farmers understand.
• Limit response to maximum 80 words.
• Use bullet points when helpful for clarity.
• Stop immediately after answering the question.
• If question is not about agriculture, briefly redirect to farming topics.{context}

Farmer Question:
{question}

Answer:"""
        
        # Optimized payload for focused, concise responses
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,  # Reduced from 0.5: less randomness, more focused
            "num_predict": 80     # Reduced from 150: prevents long irrelevant text
        }
        
        # Call the Ollama API with extended timeout for reliability
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "").strip()
            
            # Clean up response - remove common suffixes that models add
            ai_response = ai_response.split("Question:")[0].strip()
            ai_response = ai_response.split("Follow-up")[0].strip()
            
            return ai_response if ai_response else "Sorry, I couldn't generate a response. Please try again."
        else:
            return f"⚠️ Error: Unable to connect to AI service (Status: {response.status_code}). Make sure Ollama is running and the model '{MODEL_NAME}' is downloaded."
    
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. The AI service is taking too long. Please try again."
    except requests.exceptions.ConnectionError:
        return "⚠️ Cannot connect to AI service. Please ensure Ollama is running. Run: ollama serve"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ============================================================
# Crop Prediction Function
# ============================================================

def predict_crop(model, encoders, feature_names, input_data):
    """
    Make a crop prediction using the trained model.
    
    Parameters:
    -----------
    model : RandomForestClassifier
        Trained model
    encoders : dict
        Dictionary of label encoders
    feature_names : list
        Feature names used during training
    input_data : dict
        Input values from user
    
    Returns:
    --------
    str : Predicted crop name
    """
    try:
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
        
        if 'Season' in encoders:
            encoder = encoders['Season']
            input_df['Season'] = encoder.transform([input_data['season']])
        else:
            season_mapping = {'Kharif': 0, 'Rabi': 1, 'Transition': 2}
            input_df['Season'] = season_mapping.get(input_data['season'], 0)
        
        if feature_names is not None:
            input_df = input_df[list(feature_names)]
        
        prediction = model.predict(input_df)[0]
        return prediction
    
    except Exception as e:
        st.error(f"❌ Error during prediction: {str(e)}")
        return None


# ============================================================
# PAGE 1: Crop Recommendation with Seed Intelligence
# ============================================================

def show_crop_recommendation_page():
    """Display the Crop Recommendation with Seed Intelligence module."""
    
    model = load_model()
    encoders = load_encoders()
    feature_names = load_feature_names()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🌾 Crop Recommendation System")
        st.markdown("""
        Analyze your field conditions and get AI-powered crop recommendations 
        with seed intelligence and cultivation advice.
        """)
    
    st.divider()
    
    # Input Section
    st.header("📋 Enter Your Field Conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧪 Soil Nutrients (kg/ha)")
        nitrogen = st.slider("Nitrogen (N)", 0, 150, 50, 5)
        phosphorus = st.slider("Phosphorus (P)", 0, 150, 50, 5)
        potassium = st.slider("Potassium (K)", 0, 210, 50, 5)
    
    with col2:
        st.subheader("🌡️ Environmental Conditions")
        temperature = st.slider("Temperature (°C)", 0.0, 50.0, 25.0, 0.5)
        humidity = st.slider("Humidity (%)", 0.0, 100.0, 70.0, 0.5)
        ph = st.slider("Soil pH", 3.5, 10.0, 6.5, 0.1)
        rainfall = st.slider("Rainfall (mm)", 0.0, 300.0, 100.0, 5.0)
    
    st.divider()
    
    # Season and Location selection
    col1, col2 = st.columns(2)
    with col1:
        season = st.selectbox("🌾 Select Season", ["Kharif", "Rabi", "Transition"])
    with col2:
        location = st.selectbox("📍 Select Your Location", SUPPORTED_REGIONS)
    
    st.divider()
    
    # Prediction Button
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
            
            # Display Results
            st.divider()
            st.success("✅ Prediction Complete!")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"""
                ### 🌿 Recommended Crop
                # **{predicted_crop.upper()}**
                """)
            
            # Field Conditions Summary
            st.subheader("📊 Your Field Conditions Summary")
            summary_df = pd.DataFrame({
                'Parameter': ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 
                             'Temperature', 'Humidity', 'Soil pH', 'Rainfall', 'Season', 'Location'],
                'Value': [f"{nitrogen} kg/ha", f"{phosphorus} kg/ha", f"{potassium} kg/ha",
                         f"{temperature}°C", f"{humidity}%", f"{ph}", f"{rainfall} mm", season, location]
            })
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Seed Recommendations Section
            st.subheader("🌱 Recommended Seed Varieties")
            
            if seed_recommendations:
                st.success(f"✅ Found **{len(seed_recommendations)}** recommended seed varieties for {location}")
                
                for i, seed in enumerate(seed_recommendations, 1):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        ### {i}. **{seed['Variety']}**
                        
                        - **Expected Yield**: {seed['Yield_t_ha']} t/ha
                        - **Disease Resistance**: {seed['Disease_Resistance']}
                        - **Growing Period**: {seed['Duration_days']} days
                        - **Special Trait**: {seed['Special_Trait']}
                        """)
                    
                    with col2:
                        st.metric("Yield", f"{seed['Yield_t_ha']} t/ha")
                
                st.divider()
            else:
                st.info(f"ℹ️ No specific seed varieties found for {predicted_crop} in {location}.")
            
            # LLM Integration
            st.subheader("🤖 AI Farming Advice")
            
            if not is_ollama_available():
                st.warning("⚠️ LLM Service Not Available. Install Ollama to enable AI advice.")
            else:
                tab1, tab2 = st.tabs(["📋 Crop & Field Advice", "🌱 Seed Cultivation Tips"])
                
                with tab1:
                    with st.spinner("🔄 Generating AI farming advice..."):
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
                        st.success("✅ AI Advice Generated!")
                        st.markdown(advice)
                    else:
                        st.error("❌ Failed to generate advice.")
                
                with tab2:
                    if seed_recommendations and len(seed_recommendations) > 0:
                        with st.spinner("🔄 Generating seed cultivation advice..."):
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
                            st.success("✅ Seed Cultivation Advice!")
                            st.markdown(seed_advice)
                        else:
                            st.info("ℹ️ Specialized seed advice unavailable.")
                    else:
                        st.info("ℹ️ Seed cultivation advice will appear once varieties are identified.")


# ============================================================
# PAGE 2: Field Intelligence
# ============================================================

def show_field_intelligence_page():
    """Display the Field Intelligence module."""
    
    st.title("🌾 Field Intelligence Module")
    st.markdown("Analyze field conditions using image-based AI analysis and get actionable insights.")
    
    st.divider()
    
    # Input Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 Upload Field Image")
        uploaded_image = st.file_uploader("Choose a field image", type=["jpg", "jpeg", "png"])
    
    with col2:
        st.subheader("🌱 Enter Seed Information")
        seed_name = st.text_input("Enter seed or crop variety name", placeholder="e.g., RiceVar25")
    
    st.divider()
    
    if uploaded_image is None:
        st.info("👆 Please upload a field image to begin analysis.")
        return
    
    # Load and display image
    image = Image.open(uploaded_image)
    image_array = np.array(image.convert('RGB'))
    
    st.subheader("📷 Uploaded Field Image")
    st.image(image, use_column_width=True)
    
    st.divider()
    
    if seed_name == "":
        st.warning("⚠️ Please enter a seed/crop variety name.")
        return
    
    # Analysis Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Analyze Field",
            use_container_width=True,
            type="primary"
        )
    
    if analyze_button:
        st.divider()
        
        # Perform analysis
        with st.spinner("🔄 Analyzing field image..."):
            # Vegetation analysis
            vegetation_percentage, vegetation_level = analyze_vegetation_coverage(image_array)
            
            # Moisture analysis
            moisture_score, moisture_level = analyze_soil_moisture(image_array)
            
            # Health score
            health_score, health_label = calculate_field_health_score(vegetation_percentage, moisture_score)
        
        # Display Results
        st.success("✅ Field Analysis Complete!")
        
        st.subheader("📊 Field Intelligence Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Vegetation Coverage", f"{vegetation_percentage}%", vegetation_level)
        
        with col2:
            st.metric("Soil Moisture", f"{int(moisture_score)}%", moisture_level)
        
        with col3:
            st.metric("Field Health Score", f"{health_score}/10", health_label)
        
        st.divider()
        
        # Detailed Report
        st.subheader("📋 Detailed Analysis")
        
        report_data = {
            'Metric': [
                'Seed/Crop Variety',
                'Vegetation Coverage',
                'Vegetation Level',
                'Soil Moisture Score',
                'Soil Moisture Level',
                'Field Health Score',
                'Overall Status'
            ],
            'Value': [
                seed_name,
                f"{vegetation_percentage}%",
                vegetation_level,
                f"{int(moisture_score)}%",
                moisture_level,
                f"{health_score}/10",
                health_label
            ]
        }
        
        report_df = pd.DataFrame(report_data)
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # AI Field Insights
        st.subheader("🤖 AI Field Insights")
        
        with st.spinner("🔄 Generating AI insights..."):
            insights = generate_field_insights(
                seed_name=seed_name,
                vegetation_level=vegetation_level,
                vegetation_percentage=vegetation_percentage,
                moisture_level=moisture_level,
                moisture_score=moisture_score,
                health_score=health_score,
                health_label=health_label
            )
            
            st.markdown(insights)


# ============================================================
# PAGE 3: AI Insights Panel (LLM Chat)
# ============================================================

def show_ai_insights_panel():
    """Display the AI Insights Panel with LLM chat functionality."""
    
    # Title and description
    st.title("🤖 AI Insights Panel")
    st.markdown("""
    Ask questions about crops, soil, fertilizers, or field conditions.
    Get instant AI-powered farming advice from our agricultural expert.
    """)
    
    st.divider()
    
    # Initialize chat history in session state if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💬 Conversation History")
        
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(f"**Your Question:** {message['content']}")
            else:
                with st.chat_message("assistant"):
                    st.write("**AI Response:**")
                    st.markdown(message["content"])
        
        st.divider()
    else:
        st.info("💡 Start by asking your farming question below!")
        st.divider()
    
    # User input section
    st.subheader("❓ Ask Your Question")
    
    # Create columns for input and button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_input(
            "Your farming question",
            placeholder="e.g., 'Is soybean suitable for this field?' or 'What fertilizer should I use?'",
            label_visibility="collapsed"
        )
    
    with col2:
        ask_button = st.button("💬 Ask AI", use_container_width=True, type="primary")
    
    # Handle the Ask AI button
    if ask_button and user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Extract context from session state if available from previous modules
        health_score = st.session_state.get("predicted_crop", None)  # Check if crop prediction was made
        vegetation_level = None
        seed_name = None
        
        # Try to get field intelligence context
        if "field_health" in st.session_state:
            health_score = st.session_state.field_health.get("health_score")
            vegetation_level = st.session_state.field_health.get("vegetation_level")
            seed_name = st.session_state.field_health.get("seed_name")
        
        # Get AI response with spinner
        with st.spinner("🤖 AI is generating focused agricultural advice..."):
            ai_response = ask_ai_insight(
                question=user_question,
                health_score=health_score,
                vegetation_level=vegetation_level,
                seed_name=seed_name
            )
        
        # Add AI response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Rerun to display the new messages
        st.rerun()
    
    # Clear history button in sidebar
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📋 Export Chat", use_container_width=True):
            if st.session_state.chat_history:
                chat_text = "AI Insights Panel - Chat History\n"
                chat_text += "=" * 50 + "\n\n"
                for i, message in enumerate(st.session_state.chat_history, 1):
                    role = "YOU" if message["role"] == "user" else "AI EXPERT"
                    chat_text += f"[{i}] {role}:\n{message['content']}\n\n"
                st.text_area("Chat Export", value=chat_text, height=300, disabled=True)
            else:
                st.warning("No chat history to export.")


# ============================================================
# Main Application with Sidebar Navigation
# ============================================================

def main():
    """Main application with sidebar navigation."""
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🌾 AI Farm Intelligence")
        st.markdown("---")

        # Navigation Menu
        selected_page = st.radio(
            "📌 Select Module:",
            [
                "Crop Recommendation with Seed Intelligence",
                "Field Intelligence",
                "AI Insights Panel (LLM Chat)"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # LLM Status with Model Info - Fresh check (no cache)
        ollama_status = is_ollama_available()

        if ollama_status:
            st.success("LLM Ready")
            # Show which model is being used
            st.caption(f"Model: `{MODEL_NAME}`")
            model_info = {
                "neural-chat": "2.0 GB",
                "phi": "2.5 GB",
                "phi3": "2.5 GB",
                "mistral": "4.0 GB",
                "llama3": "4.6 GB"
            }
            if MODEL_NAME in model_info:
                st.caption(f"RAM: {model_info[MODEL_NAME]}")
            st.caption("AI insights enabled")
        else:
            st.warning("⚠️ LLM Offline")
            st.caption("Using offline advice mode")
            st.caption("Run: ollama serve")

        st.markdown("---")

        # Dark mode toggle
        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = False

        st.session_state.dark_mode = st.toggle(
            "Dark mode",
            value=st.session_state.dark_mode
        )

        st.markdown("---")

        # Developer tools
        with st.expander("🔧 Debug Info"):
            st.write(f"LLM Available: {ollama_status}")
            st.write(f"Model: {MODEL_NAME}")
            if st.button("🔄 Refresh LLM Status"):
                st.rerun()

        st.markdown("---")

        # Info Section
        with st.expander("ℹ️ About This App"):
            st.markdown("""
            ### AI Farm Intelligence System

            Three integrated modules for modern farming:

            **Module 1: Crop Recommendation**
            - ML-based crop prediction
            - Seed variety recommendations
            - AI cultivation advice

            **Module 2: Field Intelligence**
            - Image-based field analysis
            - Vegetation coverage detection
            - Soil moisture estimation
            - Field health scoring

            **Module 3: AI Insights Panel**
            - Chat-based farming guidance
            - Ask agriculture questions
            - Get expert AI responses

            All powered by AI and machine learning!
            """)

    if st.session_state.get("dark_mode"):
        st.markdown("""
            <style>
                .stApp {
                    background-color: #0f1115;
                    color: #ffffff;
                }
                section[data-testid="stSidebar"] {
                    background-color: #141823;
                }
                .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
                .stApp p, .stApp span, .stApp label, .stApp div,
                .stMarkdown, .stText, .stCaption, .stHeader, .stSubheader, .stTitle {
                    color: #ffffff;
                }
                .stButton>button, .stTextInput>div>div>input, .stTextArea>div>div>textarea,
                .stSelectbox>div>div>div, .stSlider>div>div>div {
                    background-color: #1b2030;
                    color: #ffffff;
                    border-color: #2a3145;
                }
                .stDataFrame, .stTable, .stMetric {
                    background-color: #1b2030;
                }
                hr {
                    border-color: #2a3145;
                }
            </style>
        """, unsafe_allow_html=True)
    
    # Display selected page
    if selected_page == "Crop Recommendation with Seed Intelligence":
        show_crop_recommendation_page()
    elif selected_page == "Field Intelligence":
        show_field_intelligence_page()
    elif selected_page == "AI Insights Panel (LLM Chat)":
        show_ai_insights_panel()


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":
    main()
