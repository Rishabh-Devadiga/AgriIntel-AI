# 🌾 AI Farm Intelligence System

An intelligent agricultural decision-support platform combining machine learning, computer vision, and LLM-powered advice for modern farming.

## 🎯 How It Works

The app has **three integrated modules**:

1. **Crop Recommendation** → User enters field conditions (soil nutrients, temperature, humidity, pH, rainfall, season) → ML model predicts best crop → Gets seed varieties & cultivation tips from AI
   
2. **Field Intelligence** → User uploads field image → AI analyzes vegetation coverage & soil moisture → Generates field health score & improvement suggestions

3. **AI Insights Panel** → Chat-based Q&A → Ask farming questions → Get context-aware advice from local LLM (phi model)

## 🚀 Quick Setup

### Prerequisites
- Python 3.9+ & pip
- Git
- Ollama ([download](https://ollama.ai)) - *Optional, for AI features*

### Installation

```bash
# Clone project
cd AgriIntel-AI

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or
source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start Ollama (optional, for LLM features)
ollama serve
# In another terminal: ollama pull phi
```

### Run App

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

## 🌐 Deploy Online

Use ngrok for instant public deployment:

```bash
# Terminal 1
streamlit run app.py

# Terminal 2 (after creating free ngrok account)
ngrok http 8501
```

Get a public URL instantly to share your app!

## 📚 Tech Stack

**Frontend**: Streamlit | **ML**: scikit-learn (Random Forest) | **Vision**: OpenCV | **LLM**: Ollama (Phi) | **Data**: Pandas, NumPy | **Visualization**: Matplotlib, Seaborn

## 📂 Project Structure

```
├── app.py                    # Main application
├── src/modules/              # Core AI modules
│   ├── llm_agent.py         # LLM integration
│   ├── seed_agent.py        # Seed recommendations
│   └── field_intelligence.py# Image analysis
├── models/                  # Trained ML models
├── data/raw/                # Datasets
└── tests/                   # Unit tests
```

## ✨ Features

- ✅ Dark mode toggle
- ✅ Real-time ML predictions
- ✅ Local LLM (no external API calls)
- ✅ Field image analysis
- ✅ Chat history export
- ✅ Production-ready code

## 🔗 Links

- 📖 Full docs: See `docs/` folder
- 🧪 Tests: `python tests/test_*.py`
- 📊 Data: `data/raw/`

## 📋 Dependencies

See `requirements.txt` for complete list:
- streamlit >= 1.28.0
- pandas >= 3.0.1
- scikit-learn >= 1.3.2
- ollama >= 0.1.0
- opencv-python >= 4.8.1
- PIL/pillow >= 10.0.1

## 🎯 Key Features

✅ Clean, organized file structure  
✅ Modular code architecture  
✅ Easy to extend with new models  
✅ Production-ready Streamlit app  
✅ Comprehensive documentation  
✅ Local LLM integration (privacy-first)  
✅ Image-based field analysis  
✅ Advanced seed recommendations  

## 🔐 Privacy

All processing happens locally:
- No data sent to external servers
- Optional Ollama runs locally
- Full control over your data

## 📝 License

See documentation in docs/ folder.

## 👨‍💼 Support

For issues or questions, refer to:
1. Documentation in `docs/` folder
2. Script help files in `scripts/`
3. Test files in `tests/` for usage examples

---

**Last Updated**: March 2026  
**Version**: 1.0.0
