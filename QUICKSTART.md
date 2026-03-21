# 🚀 Quick Setup Guide

Get your AI Crop Recommendation System running in 5 minutes!

## ⚡ Express Setup (Without LLM)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

### 3. Access
Open browser: **http://localhost:8501**

---

## 🤖 Full Setup (With AI Advice via Ollama)

### 1. Install Ollama
Download from: https://ollama.ai

### 2. Start Ollama in Terminal 1
```bash
ollama serve
```

### 3. Download Llama3 in Terminal 2
```bash
ollama pull llama3
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App in Terminal 3
```bash
streamlit run app.py
```

### 6. Access
Open browser: **http://localhost:8501**

---

## 🌾 Using the App

1. **Enter your field conditions** (soil nutrients, temperature, etc.)
2. **Click "Get Crop Recommendation"**
3. **View predicted crop**
4. **Read AI farming advice** (if Ollama is running)

---

## ❓ Having Issues?

| Issue | Solution |
|-------|----------|
| `streamlit not found` | Use: `python -m streamlit run app.py` |
| Model file not found | Check you're in the `Crop LLM` directory |
| LLM not responding | Ensure Ollama is running: `ollama serve` |
| Connection refused | Check Ollama: `curl http://localhost:11434` |

---

## 📁 File Checklist

Ensure these files are present:
- ✅ `app.py` - Main Streamlit app
- ✅ `llm_agent.py` - LLM integration
- ✅ `random_forest_crop_model.pkl` - ML model
- ✅ `label_encoders.pkl` - Encoders
- ✅ `feature_names.pkl` - Feature names
- ✅ `requirements.txt` - Dependencies
- ✅ `README.md` - Full documentation

---

## 🎯 What Happens When You Use the App

1. **You enter field data** → Streamlit receives inputs
2. **Model predicts crop** → Random Forest model (99.32% accurate)
3. **LLM generates advice** → Llama3 via Ollama (if available)
4. **Results displayed** → Crop name + farming tips

---

**Ready? Start with: `streamlit run app.py`** 🌾
