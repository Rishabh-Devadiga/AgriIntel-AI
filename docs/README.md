# 🌾 AI Crop Recommendation System

A production-ready web application that combines machine learning and local LLM integration to provide intelligent crop recommendations and farming advice.

## 🎯 Features

- **🤖 ML-Powered Crop Prediction**: Random Forest model with 99.32% accuracy
- **💬 AI Farming Advice**: Llama3 LLM provides personalized farming tips
- **📊 Field Analysis**: Evaluates soil nutrients, climate, and weather conditions
- **🌍 Multi-Crop Support**: Recommends from 22 major Indian crops
- **👨‍🌾 Farmer-Friendly Interface**: Simple web interface built with Streamlit
- **⚡ Local LLM**: Runs entirely on your machine via Ollama (no cloud dependency)

## 📋 What's Included

```
Crop LLM/
├── app.py                              # Main Streamlit application
├── llm_agent.py                        # LLM integration module (Ollama/Llama3)
├── model_train.ipynb                   # ML model training notebook
├── random_forest_crop_model.pkl        # Trained Random Forest model
├── label_encoders.pkl                  # Categorical encoders
├── feature_names.pkl                   # Feature names used in training
├── Crop_recommendation_with_season.csv # Training dataset
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Ollama (for AI advice feature)
- Virtual environment (recommended)

### Step 1: Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Ollama (for LLM features)

**Option A: With AI Advice (Recommended)**

1. Download and install Ollama: https://ollama.ai
2. In a separate terminal, start Ollama:
   ```bash
   ollama serve
   ```
3. In another terminal, download Llama3:
   ```bash
   ollama pull llama3
   ```

**Option B: Without AI Advice (Basic Mode)**

Skip the Ollama setup. The app will still work but won't generate farming advice.

### Step 4: Run the Application

```bash
streamlit run app.py
```

Your application will open at: **http://localhost:8501**

## 📱 How to Use the Web App

1. **Enter Soil Conditions**
   - Nitrogen (N): 0-150 kg/ha
   - Phosphorus (P): 0-150 kg/ha
   - Potassium (K): 0-210 kg/ha

2. **Enter Environmental Conditions**
   - Temperature: 0-50°C
   - Humidity: 0-100%
   - Soil pH: 3.5-10.0
   - Rainfall: 0-300 mm

3. **Select Season**
   - Kharif (Monsoon)
   - Rabi (Winter)
   - Transition (Spring/Summer)

4. **Get Recommendation**
   - Click "🎯 Get Crop Recommendation"
   - View predicted crop
   - Get AI-generated farming advice (if Ollama is running)

## 🤖 AI Farming Advice Features

When Ollama is running and connected, the app generates advice on:

- **Why this crop is recommended** - Based on your field conditions
- **Optimal farming practices** - Season-specific techniques
- **Fertilizer recommendations** - Customized N, P, K advice
- **Weather considerations** - Based on temperature and rainfall
- **Expected yield tips** - Practical suggestions for better harvests
- **Potential risks** - Challenges to watch for

## 🔧 Configuration

### Model Settings

Edit `app.py` to change:
- Model file path: `random_forest_crop_model.pkl`
- Encoder file path: `label_encoders.pkl`

### LLM Settings

Edit `llm_agent.py` to change:
- Ollama URL: `http://localhost:11434`
- Model name: `llama3`
- Temperature: `0.7` (0=deterministic, 1=creative)

## 📊 Model Details

- **Algorithm**: Random Forest Classifier
- **Trees**: 100
- **Max Depth**: 10
- **Training Accuracy**: 98.12%
- **Testing Accuracy**: 99.32%
- **CV Score**: 99.26% (±0.58%)
- **Data**: 2,200 samples from Indian agricultural dataset

## 🧪 Features Used

The model uses 8 features for prediction:
1. **N** - Nitrogen content (kg/ha)
2. **P** - Phosphorus content (kg/ha)
3. **K** - Potassium content (kg/ha)
4. **Temperature** (°C)
5. **Humidity** (%)
6. **pH** - Soil pH value
7. **Rainfall** (mm)
8. **Season** - Categorical (Kharif/Rabi/Transition)

## 🌾 Crops Supported (22 types)

Rice, Wheat, Maize, Chickpea, Kidneybeans, Pigeonpeas, Mothbeans, Mungbean, Blackgram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee

## 🔌 Troubleshooting

### Issue: Streamlit command not found
**Solution**:
```bash
python -m streamlit run app.py
```

### Issue: Model file not found
**Solution**:
```bash
# Ensure you're in the correct directory
cd "path/to/Crop LLM"

# Check if files exist
ls *.pkl
```

### Issue: LLM not generating advice
**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Ensure Llama3 is installed
ollama pull llama3
```

### Issue: "Connection refused" error
**Solution**:
1. Make sure Ollama is running: `ollama serve`
2. Check Ollama is accessible: `curl http://localhost:11434`
3. Restart Ollama
4. Refresh the Streamlit app

## 📈 Future Enhancements

Planned features for future versions:
- 🦠 Crop disease detection and management
- 🧪 Advanced fertilizer optimization algorithms
- 🌤️ Real-time weather-based recommendations
- 💬 Interactive farmer chatbot
- 📊 Crop market analysis and pricing
- 🎯 Yield prediction models
- 🔄 Multi-season crop rotation planning

## 🔒 Data Privacy

- **No cloud connectivity**: Everything runs locally on your machine
- **Model inference**: Uses only locally stored model files
- **LLM processing**: Ollama runs locally, no data sent to external servers
- **User inputs**: Not stored or logged

## 📚 Technical Architecture

```
┌─────────────────┐
│   Streamlit UI  │ (Web Interface for farmers)
└────────┬────────┘
         │
    ┌────▼─────┐
    │           │
    ├─► ML Model ──► Random Forest (99.32% accuracy)
    │           │
    └───────────┘
         │
    ┌────▼─────────────────┐
    │  LLM Integration      │
    ├─► Ollama ──► Llama3   │
    └─────────────────────────┘
```

## 📝 Code Structure

### `app.py` - Main Application
- Streamlit UI setup
- Model loading and caching
- Input collection
- Prediction logic
- LLM integration
- Results display

### `llm_agent.py` - LLM Module
- Ollama API integration
- Prompt engineering
- Advice generation functions
- Error handling
- Ollama availability check

### Model Training
- See `model_train.ipynb` for full training pipeline
- Includes data preprocessing, feature engineering, model evaluation
- Cross-validation and feature importance analysis

## 🤝 Contributing

To extend the system:

1. **Add new models**: Train additional models and save as `.pkl` files
2. **Add new features**: Extend input fields in `app.py` and retrain model
3. **Enhance LLM**: Create new functions in `llm_agent.py` for additional advice
4. **Improve UI**: Customize Streamlit components in `app.py`

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all files are in the correct directory
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Check Ollama is running for LLM features: `ollama serve`

## 📄 License

This project is provided as-is for agricultural AI research and development.

## 👨‍💼 Built By

Agricultural AI Solutions | 2026

---

**Happy Farming! 🌾**

Powered by Random Forest × Llama3 × Streamlit
