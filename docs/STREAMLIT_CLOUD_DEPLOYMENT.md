# Streamlit Cloud Deployment Guide

## Prerequisites
- GitHub account with the AgriIntel-AI repository
- Hugging Face API token (get it from https://huggingface.co/settings/tokens)
- Streamlit Cloud account (free at https://streamlit.io/cloud)

## Step-by-Step Deployment

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Set Up Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click **"New app"**
3. Select your GitHub repository: `AgriIntel-AI`
4. Select the branch: `main`
5. Select the file: `app.py`
6. Click **"Deploy"**

### 3. Configure HF_TOKEN Secret

Once the app is deployed:

1. Click the **three-line menu** (⋯) in the top right
2. Select **"Settings"**
3. Click on the **"Secrets"** tab
4. Add your Hugging Face token:
   ```
   HF_TOKEN = "hf_YOUR_ACTUAL_TOKEN_HERE"
   ```
5. Click **"Save"**
6. The app will automatically restart with the secret configured

### 4. Verify Deployment

- Visit your app URL (format: `https://[username]-agriintel-ai.streamlit.app`)
- Test the AI chat feature - it should now work without errors
- Try asking: "What are the benefits of crop rotation?"

## Troubleshooting

### Error: "AgriLLM is not configured"
**Solution:** Make sure you've set the `HF_TOKEN` in Streamlit Cloud Secrets (see Step 3 above)

### Error: "Invalid username or password"
**Solution:** Your HF_TOKEN is invalid or expired. Get a new one from https://huggingface.co/settings/tokens

### Error: "Error installing requirements"
**Solution:** This was fixed in requirements.txt with Pillow 11.0+ support. Try restarting the app.

## Local Development with Secrets

To test Streamlit Secrets locally:

1. Create `.streamlit/secrets.toml`:
   ```toml
   HF_TOKEN = "hf_YOUR_TOKEN_HERE"
   ```
2. Run: `streamlit run app.py`
3. The app will use the token from secrets.toml

## Security Notes

- **NEVER commit secrets.toml to GitHub** (it's in .gitignore)
- **NEVER share your HF_TOKEN** publicly
- Streamlit Cloud securely encrypts and stores your secrets
- Your token is not visible in logs or error messages

## Environment Variables Support

The app automatically detects tokens from multiple sources in this priority:
1. Streamlit Secrets (for cloud deployments)
2. Process environment variables (for local CLI)
3. Windows registry (for Windows local development)

This ensures compatibility across all deployment methods.
