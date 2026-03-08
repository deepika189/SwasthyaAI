# Complete Setup Guide for SwasthyaAI with New AWS Account

This guide will walk you through setting up SwasthyaAI from scratch with a new AWS account.

## Prerequisites

- ✓ Python 3.9 installed
- ✓ New AWS Account created
- ✓ SwasthyaAI code downloaded

---

## Part 1: AWS Account Setup (15-20 minutes)

### Step 1: Create IAM User

1. **Sign in to AWS Console**
   - Go to https://console.aws.amazon.com/
   - Sign in with your root account credentials

2. **Navigate to IAM**
   - Search for "IAM" in the top search bar
   - Click on "IAM" service

3. **Create New User**
   - Click "Users" in the left sidebar
   - Click "Create user" button
   - User name: `SwasthyaAI`
   - Click "Next"

4. **Set Permissions**
   - Select "Attach policies directly"
   - Search and select: `AmazonBedrockFullAccess`
   - (Optional) Also add: `AmazonS3FullAccess` if you want logging
   - Click "Next"
   - Click "Create user"

### Step 2: Create Access Keys

1. **Open Your User**
   - Click on the `SwasthyaAI` user you just created
   - Go to "Security credentials" tab

2. **Create Access Key**
   - Scroll down to "Access keys" section
   - Click "Create access key"
   - Select use case: "Local code"
   - Check the confirmation box
   - Click "Next"
   - Description: `SwasthyaAI Local Development`
   - Click "Create access key"

3. **Save Your Credentials** ⚠️ IMPORTANT
   - Copy the "Access key ID" (starts with AKIA...)
   - Copy the "Secret access key" (shown only once!)
   - Click "Download .csv file" as backup
   - Click "Done"

### Step 3: Verify Bedrock Model Access

**Good News!** AWS has simplified Bedrock access. Models are now automatically enabled when first invoked.

1. **Go to Bedrock Console**
   - Search for "Bedrock" in the top search bar
   - Click on "Amazon Bedrock"
   - **IMPORTANT:** Make sure region is set to `US East (N. Virginia) us-east-1` in top-right corner

2. **Check Model Catalog (Optional)**
   - Click "Model catalog" in the left sidebar
   - Verify these models are available:
     - ✓ "Titan Text Embeddings V2" (by Amazon) - Use this instead of V1
     - ✓ "Titan Embed Text V1" (by Amazon) - Alternative name
     - ✓ "Claude 3 Haiku" (by Anthropic)
   
3. **First-Time Anthropic Users**
   - If this is your first time using Anthropic models (Claude), you may need to:
     - Submit use case details when you first invoke the model
     - This happens automatically when you start the backend
     - You'll receive a prompt or email if additional information is needed

4. **Alternative Embedding Models**
   - If `amazon.titan-embed-text-v2:0` is not available in your region, you can use:
     - `amazon.titan-embed-text-v1` (older version)
     - `cohere.embed-english-v3` (Cohere alternative)
     - `cohere.embed-multilingual-v3` (for multilingual support)
   - Update the model ID in your `.env` file under `RAG_EMBEDDINGS_MODEL`

5. **No Manual Activation Required**
   - The old "Model access" page has been retired
   - Models activate automatically on first use
   - Your IAM permissions control access (already set in Step 1)

---

## Part 2: Local Environment Setup (10 minutes)

### Step 4: Install Python Dependencies

1. **Open Command Prompt/Terminal**
   - Navigate to your SwasthyaAI project folder:
   ```cmd
   cd "D:\Swasthya AI - Prototype - RAG"
   ```

2. **Install Required Packages**
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Fix Numpy Compatibility** (if needed)
   ```cmd
   pip install "numpy<2.0.0" --force-reinstall
   ```

### Step 5: Configure Environment Variables

1. **Edit the .env file**
   - Open `.env` file in your project folder
   - Replace the placeholder values:

   ```env
   # AWS Configuration
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIA...your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here

   # Bedrock Configuration
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

   # Model Paths
   MODEL_PATH=models/best_model.joblib

   # Dataset Path
   DATASET_PATH=data/disease_symptom_dataset.csv

   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000

   # RAG System Configuration
   RAG_ENABLED=true
   RAG_PDF_PATH=data/The complete book of Ayurvedic home remedies.pdf
   RAG_INDEX_PATH=data/faiss_index
   RAG_CHUNK_SIZE=1000
   RAG_CHUNK_OVERLAP=200
   RAG_TOP_K=3
   RAG_EMBEDDINGS_MODEL=amazon.titan-embed-text-v2:0
   RAG_LLM_MODEL=anthropic.claude-3-haiku-20240307-v1:0
   ```

2. **Save the file**

### Step 6: Train the ML Model

1. **Run Training Script**
   ```cmd
   python scripts/train_model.py
   ```

2. **Wait for Completion**
   - This will take 1-2 minutes
   - You should see: "✓ Training successful! Best model: RandomForest"
   - Model files will be saved in `models/` folder

---

## Part 3: Running SwasthyaAI (5 minutes)

### Step 7: Start the Backend API

1. **Open First Terminal/Command Prompt**
   ```cmd
   python start_backend.py
   ```

2. **Wait for Initialization**
   - You'll see logs showing components initializing
   - RAG system will process the PDF (takes 2-3 minutes first time)
   - Wait until you see: "ALL COMPONENTS INITIALIZED SUCCESSFULLY ✓"
   - Server will be running at: http://localhost:8000

3. **Verify Backend is Running**
   - Open browser: http://localhost:8000/health
   - Should show: `{"status":"healthy","model_loaded":true,"version":"1.0.0"}`

### Step 8: Start the UI

1. **Open Second Terminal/Command Prompt**
   - Navigate to project folder again:
   ```cmd
   cd "D:\Swasthya AI - Prototype - RAG"
   ```

2. **Start Streamlit UI**
   ```cmd
   python start_ui.py
   ```
   Or:
   ```cmd
   streamlit run ui/app.py
   ```

3. **Access the Application**
   - Browser should open automatically
   - If not, go to: http://localhost:8501
   - You should see the SwasthyaAI interface

---

## Part 4: Testing the Application

### Step 9: Test Symptom Analysis

1. **In the UI, enter symptoms** (English or Hindi):
   - Example 1: "I have fever, headache, and body pain"
   - Example 2: "mujhe bukhar aur sar dard hai"

2. **Click "Analyze Symptoms"**

3. **Review Results**:
   - ✓ Extracted symptoms
   - ✓ Top 3 disease predictions with probabilities
   - ✓ Risk level assessment
   - ✓ Referral recommendation
   - ✓ Ayurvedic remedies (from RAG system)

---

## Troubleshooting

### Issue 1: "AccessDeniedException" Error

**Problem:** AWS credentials don't have Bedrock permissions

**Solution:**
1. Go to AWS IAM Console
2. Click on user `SwasthyaAI`
3. Verify policy `AmazonBedrockFullAccess` is attached
4. If not, add it under "Permissions" tab

**Note:** Model access is now automatic on first use. If you get AccessDenied, it's an IAM permission issue, not model access.

### Issue 2: "Model not loaded" Error

**Problem:** ML model files missing

**Solution:**
```cmd
python scripts/train_model.py
```

### Issue 3: Port 8000 Already in Use

**Problem:** Another process is using port 8000

**Solution:**
```cmd
netstat -ano | findstr :8000
taskkill /F /PID <process_id>
```

### Issue 4: RAG System Fails to Initialize

**Problem:** PDF processing or embeddings error

**Solution 1 - Throttling Error (Too many requests):**
- This happens when processing large PDFs on new AWS accounts
- The system will retry automatically with delays
- If it still fails, wait 5-10 minutes and restart the backend
- The embeddings are cached after first successful run

**Solution 2 - Disable RAG temporarily:**
- Edit `.env` file
- Set: `RAG_ENABLED=false`
- Restart backend

**Solution 3 - Check Bedrock access:**
- Verify IAM user has `AmazonBedrockFullAccess` policy
- Check AWS credentials in `.env` are correct
- Models activate automatically on first use

**Solution 4 - Use cached index (if available):**
- If you've successfully built the index before, it's saved in `data/faiss_index/`
- The system will load from cache on subsequent starts (much faster)

### Issue 5: Numpy/Sklearn Compatibility Error

**Problem:** Version mismatch between numpy and scikit-learn

**Solution:**
```cmd
pip install "numpy<2.0.0" --force-reinstall
pip install --upgrade scikit-learn
python scripts/train_model.py
```

---

## Quick Start Commands (After Initial Setup)

Once everything is configured, you only need these commands:

**Terminal 1 - Backend:**
```cmd
cd "D:\Swasthya AI - Prototype - RAG"
python start_backend.py
```

**Terminal 2 - UI:**
```cmd
cd "D:\Swasthya AI - Prototype - RAG"
python start_ui.py
```

---

## Architecture Overview

```
┌─────────────────┐
│   Streamlit UI  │ (Port 8501)
│   (Frontend)    │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│   FastAPI       │ (Port 8000)
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌─────┐  ┌──────┐  ┌──────────┐
│Bedrock │ │ ML  │  │ RAG  │  │  Risk    │
│(AWS)   │ │Model│  │System│  │ Engine   │
└────────┘ └─────┘  └──────┘  └──────────┘
```

---

## Cost Estimation (AWS)

**Bedrock Pricing (us-east-1):**
- Titan Embeddings: $0.0001 per 1K tokens
- Claude 3 Haiku: $0.00025 per 1K input tokens, $0.00125 per 1K output tokens

**Estimated Monthly Cost for Development:**
- ~100 queries/day: $2-5/month
- First-time PDF processing: ~$0.50 (one-time)

**Free Tier:**
- AWS Free Tier doesn't include Bedrock
- But costs are very low for development/testing

---

## Next Steps

1. ✓ Test with various symptoms
2. ✓ Review Ayurvedic remedies output
3. ✓ Check logs in terminal for debugging
4. ✓ Customize prompts in `app/bedrock_integration.py`
5. ✓ Add more medical data to improve predictions

---

## Support Files

- `README.md` - Project overview
- `AWS_BEDROCK_SETUP.md` - Detailed Bedrock setup
- `RAG_INTEGRATION_SUMMARY.md` - RAG system details
- `SYSTEM_FLOWCHART.md` - System architecture

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to Git (it contains secrets)
- Keep AWS credentials secure
- Use IAM roles instead of access keys in production
- Enable MFA on your AWS account
- Regularly rotate access keys

---

## Success Checklist

- [ ] AWS account created
- [ ] IAM user created with Bedrock access
- [ ] Access keys generated and saved
- [ ] Bedrock console verified (models auto-enable on first use)
- [ ] Python dependencies installed
- [ ] .env file configured with AWS credentials
- [ ] ML model trained successfully
- [ ] Backend starts without errors
- [ ] UI accessible at localhost:8501
- [ ] Test query returns predictions and remedies

---

**Congratulations! SwasthyaAI is now running! 🎉**

For issues or questions, check the troubleshooting section above.
