# 🚨 LLM Memory Fix - Setup Instructions

## Problem
```
❌ Error: "model requires more system memory (4.6 GiB) than is available (3.4 GiB)"
```

Your system doesn't have enough RAM for the full `llama3` model (4.6GB required).

---

## ✅ Solution: Use Lightweight Model

The app now automatically detects your available memory and switches to a lightweight model.

### Step 1: Pull a lightweight model

Choose ONE based on your RAM:

**Option A: For 3-4 GB RAM (RECOMMENDED)**
```bash
# In PowerShell/Command Prompt with Ollama installed:
ollama pull neural-chat
```
- **Size**: ~2.0 GB
- **Speed**: Fast
- **Quality**: Good (specializes in chat/advice)

**Option B: Alternative lightweight model**
```bash
ollama pull phi
```
- **Size**: ~2.5 GB
- **Speed**: Very fast
- **Quality**: Good

**Option C: If you have 4+ GB RAM**
```bash
ollama pull mistral
```
- **Size**: ~4.0 GB 
- **Speed**: Moderate
- **Quality**: Excellent

### Step 2: Set up Ollama

```bash
# Open PowerShell, run:
ollama serve
```

Keep this running in the background while using the app.

### Step 3: Run the app

```bash
cd "c:\Users\Rishabh\OneDrive\Crop LLM"
& ".\.venv\Scripts\Activate.ps1"
streamlit run app.py
```

---

## 🔍 How It Works Now

The system automatically:

1. ✅ Detects which models you have installed
2. ✅ Selects the best model for your system memory
3. ✅ Falls back to offline advice if LLM fails
4. ✅ Shows helpful error messages with solutions

**Priority order (automatic selection):**
1. `neural-chat` (2.0 GB) ← Best for low RAM
2. `phi` (2.5 GB) ← Alternative
3. `mistral` (4.0 GB) ← Better quality if space available
4. `llama3` (4.6 GB) ← Full power if RAM available

---

## 📊 Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **neural-chat** | 2.0 GB | ⚡⚡⚡ Fast | 4/5 | 3-4 GB RAM ✓ |
| **phi** | 2.5 GB | ⚡⚡⚡ Fast | 4/5 | 3-4 GB RAM |
| **mistral** | 4.0 GB | ⚡⚡ Moderate | 5/5 | 4+ GB RAM |
| llama3 | 4.6 GB | ⚡ Slower | 5/5 | 5+ GB RAM |

---

## 🛠️ Troubleshooting

### Still getting memory error after installing neural-chat?

**Step 1: Stop Ollama**
```bash
# In the Ollama terminal, press Ctrl+C
```

**Step 2: Clear model cache**
```bash
# Remove old model (if you want to save space)
ollama rm llama3

# OR keep it and just use neural-chat
```

**Step 3: Restart Ollama**
```bash
ollama serve
```

**Step 4: Run app**
```bash
streamlit run app.py
```

---

### Model not showing up?

**Check installed models:**
```bash
ollama list
```

**Should show output like:**
```
NAME             ID              SIZE    MODIFIED
neural-chat:latest  1a2b3c4d5e6f  2.0 GB  2 hours ago
```

---

### App still showing "LLM Service Not Available"?

1. **Ensure Ollama is running** → See "Step 2" above
2. **Check Ollama is on port 11434:**
   ```bash
   netstat -an | findstr 11434
   ```
3. **Restart Ollama completely:**
   - Kill process
   - Wait 3 seconds  
   - Run `ollama serve` again

---

## 💾 Free Up More Memory

If you still want `llama3` or `mistral`:

**Close unnecessary apps:**
- Web browsers (especially Chrome/Firefox)
- Video/music streaming
- Gaming apps
- Large applications

**Restart your computer:**
```bash
# Clears system cache, frees RAM
```

**Check available RAM:**
```bash
# In PowerShell:
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory
```

---

## 🎯 Quick Start Command

After installing neural-chat:

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run the app (wait 5 seconds after Terminal 1)
cd "c:\Users\Rishabh\OneDrive\Crop LLM"
& ".\.venv\Scripts\Activate.ps1"
streamlit run app.py
```

---

## ✨ What Changes for You

- ✅ App automatically picks best model
- ✅ Fast performance with neural-chat
- ✅ Same AI farming advice quality
- ✅ Graceful fallback if LLM fails
- ✅ Better error messages

---

## 📋 Verification

Run this to verify everything works:

```bash
cd "c:\Users\Rishabh\OneDrive\Crop LLM"
& ".\.venv\Scripts\Activate.ps1"
python diagnose_ollama.py
```

Should show:
```
✅ Ollama Service: RUNNING
✅ Models: Available
✅ Basic Generation: WORKING
✅ Field Intelligence: WORKING
```

---

**Recommended: Install `neural-chat` → Restart → Done!** 🌾
