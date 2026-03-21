# 🌾 AgriIntel-AI Farm Intelligence System

A production-ready agricultural AI system with three integrated modules for modern farming.

## 📁 Project Structure

```
AgriIntel-AI/
├── src/                              # Source code package
│   ├── __init__.py                  # Package initialization
│   ├── modules/                     # Core AI modules
│   │   ├── __init__.py             # Modules package
│   │   ├── llm_agent.py            # LLM integration (Ollama)
│   │   ├── seed_agent.py           # Seed intelligence
│   │   └── field_intelligence.py   # Image-based field analysis
│
├── models/                          # Trained ML models
│   ├── random_forest_crop_model.pkl       # Crop prediction model
│   ├── label_encoders.pkl                 # Feature encoders
│   └── feature_names.pkl                  # Model feature names
│
├── data/                            # Data files
│   ├── raw/                        # Raw data
│   │   ├── seed_varieties_200_rows.csv
│   │   ├── Crop_recommendation.csv
│   │   └── Crop_recommendation_with_season.csv
│   └── processed/                  # Processed data (for future use)
│
├── notebooks/                       # Jupyter notebooks
│   ├── model_train.ipynb           # Model training
│   └── EDA.ipynb                   # Exploratory data analysis
│
├── docs/                           # Documentation
│   ├── README.md                   # Original project README
│   ├── QUICKSTART.md               # Quick start guide
│   ├── USER_GUIDE.md               # User guide
│   └── *.md                        # Other documentation
│
├── tests/                          # Test files
│   ├── test_llm_*.py              # LLM tests
│   ├── test_field_*.py            # Field intelligence tests
│   └── test_seed_*.py             # Seed agent tests
│
├── scripts/                        # Utility scripts
│   ├── check_llm_status.py        # LLM diagnostics
│   ├── diagnose_ollama.py         # Ollama diagnostics
│   └── compare_models.py          # Model comparison
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                # Streamlit settings
│
├── app.py                         # Main Streamlit application (entry point)
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Ollama (for AI features) - [Download](https://ollama.ai)

### Setup

1. **Clone/Navigate to Project**
   ```bash
   cd AgriIntel-AI
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate   # macOS/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Ollama (Optional - for AI features)**
   ```bash
   ollama serve
   ```
   In another terminal:
   ```bash
   ollama pull phi  # or neural-chat, mistral, llama3
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

## 📚 Modules

### 1. Crop Recommendation with Seed Intelligence
- **Location**: `src/modules/llm_agent.py` + `src/modules/seed_agent.py`
- **Features**:
  - ML-based crop prediction (99.32% accuracy)
  - Seed variety recommendations
  - LLM-powered cultivation advice
  - Crop-specific farming tips

### 2. Field Intelligence
- **Location**: `src/modules/field_intelligence.py`
- **Features**:
  - Image-based field analysis
  - Vegetation coverage detection
  - Soil moisture estimation
  - Field health scoring
  - AI-powered field insights

### 3. AI Insights Panel
- **Location**: `app.py` (ask_ai_insight function)
- **Features**:
  - Chat-based farming Q&A
  - Context-aware advice
  - Agriculture-focused responses
  - Chat history export

## 🔧 Configuration

### Streamlit Config (.streamlit/config.toml)
- Customizable theme colors
- Logger level settings
- Client toolbar configuration

### Models Directory (models/)
- `random_forest_crop_model.pkl`: Trained Random Forest classifier
- `label_encoders.pkl`: Categorical feature encoders
- `feature_names.pkl`: Feature names for model input

### Data Directory (data/)
- **raw/**: Original CSV datasets
- **processed/**: Prepared data (for future pipelines)

## 📊 Data Files

### Crop Recommendation Data
- `Crop_recommendation.csv`: Crop recommendations by soil parameters
- `Crop_recommendation_with_season.csv`: Season-aware recommendations

### Seed Data
- `seed_varieties_200_rows.csv`: Seed varieties with yield, disease resistance, and traits

## 🧪 Testing

Run tests from the tests/ directory:
```bash
python tests/test_field_intelligence.py
python tests/test_llm_direct.py
python tests/test_seed_agent.py
```

## 📖 Documentation

See `docs/` folder for:
- `README.md` - Original project documentation
- `QUICKSTART.md` - Quick setup guide
- `USER_GUIDE.md` - Detailed user guide
- `LLM_SETUP_GUIDE.md` - LLM configuration
- `IMPLEMENTATION_SUMMARY.md` - Implementation details

## ⚙️ Troubleshooting

### Issue: Models not found
**Solution**: Ensure model files are in `models/` directory. Run setup from Project Structure section.

### Issue: LLM offline
**Solution**: 
```bash
ollama serve  # Start Ollama service
ollama pull phi  # Download model
```

### Issue: Module imports failing
**Solution**: Ensure you're running from project root:
```bash
cd AgriIntel-AI
streamlit run app.py
```

### Issue: Seed data not found
**Solution**: Verify `data/raw/seed_varieties_200_rows.csv` exists.

## 🔄 Updating Imports

The application automatically adds `src/` to the Python path in `app.py`:
```python
sys.path.insert(0, str(Path(__file__).parent / "src"))
from modules.llm_agent import ...
```

If you create new modules, place them in `src/modules/` and import from there.

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
