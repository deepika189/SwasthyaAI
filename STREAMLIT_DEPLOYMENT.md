# SwasthyaAI Lite - Streamlit Cloud Deployment Guide

This guide will help you deploy SwasthyaAI Lite to Streamlit Cloud.

## 📋 Prerequisites

1. GitHub account
2. Streamlit Cloud account (free at https://share.streamlit.io/)
3. AWS credentials (optional - can use mock mode)

---

## 🚀 Quick Deployment Steps

### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit for Streamlit deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repository
4. Configure:
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 3.9 or higher
   - **Requirements file**: `requirements_streamlit.txt` (optional, will auto-detect)

### Step 3: Configure Secrets (AWS Credentials)

In Streamlit Cloud app settings:

1. Click "Advanced settings" → "Secrets"
2. Add your configuration:

**Option A: Use Mock Mode (No AWS Required)**
```toml
USE_MOCK_BEDROCK = "true"
AWS_REGION = "us-east-1"
```

**Option B: Use Real AWS Bedrock**
```toml
USE_MOCK_BEDROCK = "false"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_HERE"
AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY_HERE"
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
```

3. Click "Save"

### Step 4: Deploy!

Click "Deploy" and wait for the app to build and launch.

---

## 🔧 Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements_streamlit.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open at http://localhost:8501

---

## 📁 Required Files for Deployment

Make sure these files are in your repository:

```
├── streamlit_app.py          # Main Streamlit app
├── requirements_streamlit.txt # Dependencies
├── app/
│   ├── bedrock_integration.py
│   ├── symptom_mapper.py
│   ├── ml_predictor.py
│   ├── risk_engine.py
│   └── data_loader.py
├── models/
│   ├── best_model.joblib
│   ├── feature_columns.joblib
│   └── label_encoder.joblib
└── data/
    └── disease_symptom_dataset.csv
```

---

## 🔐 Security Notes

1. **Never commit AWS credentials** to GitHub
2. Always use Streamlit Secrets for sensitive data
3. Add `.env` to `.gitignore`
4. Use IAM roles with minimal permissions

---

## 💰 Cost Considerations

### Mock Mode (Free)
- No AWS costs
- Uses keyword-based symptom extraction
- Good for testing and demos

### Real Bedrock Mode
- AWS Bedrock charges apply
- Claude 3 Haiku: ~$0.25 per 1M input tokens
- Estimated: $3-15/month for moderate usage
- Set up AWS Budget alerts

---

## 🐛 Troubleshooting

### "Module not found" error
- Check `requirements_streamlit.txt` includes all dependencies
- Verify file paths are correct

### "Model file not found" error
- Ensure `models/` directory is committed to GitHub
- Model files must be in the repository

### AWS credentials not working
- Verify secrets are correctly formatted in Streamlit Cloud
- Check IAM permissions for Bedrock access
- Try mock mode first to isolate the issue

### App is slow
- Streamlit Cloud free tier has limited resources
- Consider caching with `@st.cache_resource`
- Mock mode is faster than real Bedrock

---

## 🎯 Testing Your Deployment

Once deployed, test with these inputs:

1. **English**: "Patient has fever, headache, and body pain"
2. **Hindi**: "Mujhe bukhar aur sir dard hai"
3. **Mixed**: "Patient ko bukhar and headache hai"

Expected: Symptoms extracted, predictions shown, risk assessment displayed

---

## 📊 Monitoring

### Streamlit Cloud Dashboard
- View app logs
- Monitor resource usage
- Check deployment status

### AWS CloudWatch (if using real Bedrock)
- Monitor API calls
- Track costs
- Set up alarms

---

## 🔄 Updating Your App

To update the deployed app:

```bash
git add .
git commit -m "Update description"
git push
```

Streamlit Cloud will automatically redeploy.

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed with correct file path
- [ ] Secrets configured (mock or real AWS)
- [ ] Model files included in repository
- [ ] App tested with sample inputs
- [ ] AWS budget alerts set (if using Bedrock)

---

## 🎉 Success!

Your SwasthyaAI Lite app is now live and accessible via a public URL!

Share the URL with ASHA workers and healthcare professionals.

---

## 📞 Support

For deployment issues:
- Streamlit Community Forum: https://discuss.streamlit.io/
- Streamlit Docs: https://docs.streamlit.io/
- AWS Bedrock Docs: https://docs.aws.amazon.com/bedrock/
