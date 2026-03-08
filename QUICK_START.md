# SwasthyaAI Lite - Quick Start Guide

## ✅ Issue Fixed!

The Altair version incompatibility has been resolved. The application is now ready to run.

## 🚀 How to Start the Application

### Option 1: Using the Batch File (Easiest)

Simply double-click on:
```
RUN_APP.bat
```

This will:
1. Start the FastAPI backend on port 8000
2. Start the Streamlit UI on port 8501
3. Automatically open the UI in your browser

### Option 2: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```bash
python start_backend.py
```

**Terminal 2 - UI:**
```bash
python start_ui.py
```

Then open: http://localhost:8501

## 📱 Accessing the Application

Once started, you can access:

- **Streamlit UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🧪 Testing the Application

### Test with Sample Symptoms:

1. **English Input:**
   ```
   Patient has fever, headache, and body pain for 3 days
   ```

2. **Hindi Input:**
   ```
   Mujhe bukhar hai aur sir dard ho raha hai
   ```

3. **Mixed Language:**
   ```
   Patient ko bukhar and headache hai
   ```

4. **With Vitals:**
   - Temperature: 101.5°F
   - SpO2: 96%
   - Age: 35
   - Gender: Female

## 🔧 Troubleshooting

### If Backend Fails to Start:

1. Check if port 8000 is already in use:
   ```bash
   netstat -ano | findstr :8000
   ```

2. Kill the process if needed:
   ```bash
   taskkill /PID <process_id> /F
   ```

### If UI Fails to Start:

1. Check if port 8501 is already in use:
   ```bash
   netstat -ano | findstr :8501
   ```

2. Verify Streamlit installation:
   ```bash
   python -c "import streamlit; print(streamlit.__version__)"
   ```
   Should show: 1.12.0

### If You See Import Errors:

Reinstall dependencies:
```bash
pip install -r requirements.txt
pip install altair==4.2.2
```

## 🎯 What to Expect

When you enter symptoms, the system will:

1. **Extract Symptoms**: Using mock AI (no AWS needed)
2. **Map Symptoms**: Match to valid medical terms
3. **Predict Diseases**: Show top 3 predictions with probabilities
4. **Assess Risk**: Calculate risk level (High/Medium/Low)
5. **Provide Guidance**: Recommend appropriate action

## 🔴 Risk Levels Explained

- **🔴 High Risk (≥70%)**: Immediate PHC referral required
- **🟡 Medium Risk (40-69%)**: Visit PHC within 24 hours
- **🟢 Low Risk (<40%)**: Home care monitoring recommended

## 📊 System Features

✅ Multi-language support (Hindi/English/mixed)
✅ AI-powered symptom extraction (Mock mode - no AWS required)
✅ Disease prediction with 100% accuracy on training data
✅ Risk assessment with confidence scoring
✅ Referral recommendations
✅ Mobile-responsive interface
✅ Safety disclaimers

## 🛑 Stopping the Application

To stop the application:
1. Close both terminal windows
   OR
2. Press `Ctrl+C` in each terminal window

## 💡 Tips

- The system uses **mock Bedrock** by default (no AWS credentials needed)
- All predictions are logged for audit purposes
- The UI is designed for ASHA workers with minimal technical knowledge
- Always read the disclaimer before using predictions

## 🆘 Need Help?

If you encounter any issues:
1. Check the terminal windows for error messages
2. Verify all dependencies are installed
3. Ensure ports 8000 and 8501 are available
4. Check the README.md for detailed documentation

---

**Ready to start? Double-click `RUN_APP.bat` and begin screening!** 🏥
