# 🌾 AI Farm Intelligence System

An intelligent agricultural platform that combines machine learning, computer vision, and LLM technology to provide data-driven crop recommendations and farming insights.

## Project Link : https://agriintel-ai.streamlit.app/

## 📌 Project Overview

This project demonstrates the integration of multiple AI/ML techniques to solve real-world agricultural problems. Farmers face challenges in crop selection, seed optimization, and field health assessment. This system addresses these through:

1. **ML-based Crop Recommendation** - Predicts optimal crops based on soil and environmental factors
2. **AI-Powered Farming Advice** - Provides intelligent guidance through fine-tuned LLM
3. **Computer Vision Analysis** - Analyzes field images to assess vegetation and soil health
4. **Seed Intelligence** - Recommends seed varieties with performance metrics

## 🎯 Core Intelligence

### Crop Recommendation Engine
- **Model**: Random Forest Classifier trained on 2,200+ agricultural samples
- **Accuracy**: 99.32% (test set)
- **Input Features**: 
  - Soil nutrients: Nitrogen (N), Phosphorus (P), Potassium (K)
  - Climate: Temperature, Humidity, pH, Rainfall
  - Temporal: Season (Kharif/Rabi/Transition)
- **Output**: Optimal crop from 22 major Indian varieties

**How It Works**: The RF model learns patterns from historical data showing which crop combinations succeed under specific soil and weather conditions. For a farmer's input, it evaluates all feature combinations and predicts the best match.

**⚠️ Important Limitation**: The model is trained on historical crop-soil-climate correlations but does NOT understand the underlying agronomic science of why certain crops need specific conditions. It learns statistical patterns from data (e.g., "rice appeared in records with high rainfall") but lacks knowledge of biological requirements (e.g., "rice needs standing water for photosynthesis"). This means:
- Recommendations are based on historical success patterns, not scientific crop requirements
- May miss edge cases where traditional practices work despite unfavorable conditions
- Requires domain expert validation for novel soil-climate combinations
- Works best when input conditions match the training dataset distribution

### Field Intelligence Module
- **Vision Analysis**: OpenCV-based image processing for field assessment

**Vegetation Coverage Detection**
- **Technique**: HSV color space filtering
- **Process**: Converts RGB image to HSV and detects green pixels using hue range (35-85)
- **Output**: Percentage of vegetation coverage
- **Classification**: Healthy (>50%), Moderate (25-50%), Low (<25%)

**Soil Moisture Estimation**
- **Technique**: Grayscale brightness analysis
- **Principle**: Darker soil indicates higher moisture; lighter soil indicates drier conditions
- **Process**: Converts image to grayscale, calculates average brightness, inverts scale (darker = more moisture)
- **Output**: Moisture score (0-100%)
- **Classification**: High (>60%), Medium (30-60%), Low (<30%)

**Field Health Scoring**
- **Formula**: (Vegetation × 0.6) + (Moisture × 0.4)
- **Weights**: Vegetation (60% - primary indicator), Moisture (40% - supporting indicator)
- **Output**: 0-10 scale with labels
- **Classification**: Healthy (≥7.0), Moderate (4.0-6.9), Poor (<4.0)

**AI Insights**: Vision data combined with ML crop predictions to generate contextual farming recommendations (e.g., irrigation timing, pest monitoring strategies)

### Seed Recommendation System
- **Database**: 200+ seed varieties with characteristics
- **Recommendations Based On**:
  - Predicted crop
  - Regional suitability
  - Disease resistance profiles
  - Expected yield potential
  - Drought/flood tolerance

### LLM Integration (AgriLLM)
- **Model**: AI71ai/Llama-agrillm-3.3-70B (fine-tuned for agriculture)
- **Purpose**: Generate contextual farming advice beyond template-based responses
- **Context Awareness**: Takes field conditions and recommendations as input
- **Fallback Intelligence**: Rule-based system provides recommendations when LLM unavailable

## 🏗️ Technical Architecture

```
┌─────────────────────┐
│  Streamlit Frontend  │ (Farmer-friendly UI)
└──────────┬──────────┘
           │
    ┌──────┴──────────────────┐
    │                         │
┌───▼────────┐        ┌──────▼──────┐
│ ML Pipeline│        │Vision Module │
├─────────────┤        ├──────────────┤
│ • RF Model  │        │ • OpenCV     │
│ • 99.32% Acc│        │ • CNN Conv   │
│ • 8 features│        │ • Health Score
└───┬────────┘        └──────┬──────┘
    │                         │
    └──────────┬──────────────┘
               │
        ┌──────▼──────────┐
        │ LLM Integration │
        ├─────────────────┤
        │ • AgriLLM       │
        │ • HuggingFace   │
        │ • Intelligent   │
        │   Fallback      │
        └─────────────────┘
```

## 📊 Model Performance

| Component | Metric | Value |
|-----------|--------|-------|
| Crop Recommendation | Test Accuracy | 99.32% |
| | CV Score | 99.26% (±0.58%) |
| | Training Data | 2,200 samples |
| Field Analysis | Vision Coverage Detection | 95%+ precision |
| | Health Scoring | 0-10 scale |
| Seed Recommendations | Database Size | 200+ varieties |

## 🌾 Supported Crops (22 varieties)

Rice, Wheat, Maize, Chickpea, Kidneybeans, Pigeonpeas, Mothbeans, Mungbean, Blackgram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute

## 🔧 Tech Stack

| Category | Technologies |
|----------|---------------|
| **Frontend** | Streamlit |
| **ML/AI** | scikit-learn, HuggingFace, LLM |
| **Vision** | OpenCV, PIL |
| **Data** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |

## 🎨 Key Features

- **Smart Crop Selection** - ML model analyzes 8 input parameters to recommend optimal crop
- **Context-Aware Advice** - LLM generates farming tips specific to field conditions
- **Visual Field Analysis** - Computer vision assesses field health from images
- **Seed Intelligence** - Recommends varieties matching predicted crop and region
- **Fallback Intelligence** - Provides recommendations even without external LLM
- **Responsive UI** - Streamlit interface optimized for farmers

## 💡 How Recommendations Work

**Example: Farmer's Query**
- Input: N=80, P=50, K=40, Temp=25°C, Humidity=75%, pH=6.8, Rainfall=120mm, Season=Kharif
- **ML Process**: RF model evaluates feature combinations from training data
- **Output**: "Rice" (matched patterns show rice thrives in these conditions)
- **AI Enhancement**: LLM generates context-specific tips:
  - Why rice is optimal for Kharif season
  - Recommended planting density
  - Irrigation schedule
  - Expected yield ranges
  - Risk factors to monitor

## 📈 Real-World Application

This system helps farmers by:
1. **Reducing Decision Uncertainty** - Data-driven recommendations vs. traditional guessing
2. **Optimizing Resource Use** - Matching crops to available soil nutrients and climate
3. **Improving Yields** - Fine-tuned seed selection based on field conditions
4. **Preventing Failures** - Warnings about unfavorable conditions for recommended crops
5. **Knowledge Transfer** - AI provides expertise normally requiring agronomists

---

**Portfolio Note**: This project demonstrates proficiency in ML (scikit-learn), deep learning (LLM integration), computer vision (OpenCV), full-stack development (Streamlit), and production engineering (fallback systems, error handling).
