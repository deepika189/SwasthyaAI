# AWS Bedrock Integration Guide

This guide will help you integrate SwasthyaAI Lite with Amazon Bedrock for real AI-powered symptom extraction.

## 📋 Prerequisites

1. **AWS Account** with Bedrock access
2. **AWS CLI** installed
3. **IAM permissions** for Bedrock
4. **Python boto3** library (already installed)

---

## 🔧 Step 1: Set Up AWS Account

### 1.1 Enable Bedrock Access (Updated Process)

**Good News!** AWS Bedrock models are now automatically enabled when first invoked. You no longer need to manually request access through the console.

**What this means:**
- Models are enabled automatically on first use
- No waiting for approval (in most cases)
- Instant access in all AWS commercial regions

**Important Notes:**
- **For Anthropic Claude models**: First-time users may need to submit use case details
- **For AWS Marketplace models**: A user with AWS Marketplace permissions must invoke the model once
- **IAM permissions**: You still need proper IAM policies (covered in Step 3)

### 1.2 Verify Bedrock Service Availability

1. Log in to AWS Console: https://console.aws.amazon.com
2. Navigate to **Amazon Bedrock** service
3. Go to **Model catalog** in the left sidebar
4. Search for **Claude 3 Haiku**
5. You should see: `anthropic.claude-3-haiku-20240307-v1:0`

### 1.3 Test Model Access (Optional)

You can test if the model is accessible using AWS CLI:

```bash
aws bedrock list-foundation-models --region us-east-1 --query "modelSummaries[?contains(modelId, 'claude-3-haiku')]"
```

Expected output:
```json
[
    {
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "modelName": "Claude 3 Haiku",
        "providerName": "Anthropic"
    }
]
```

### 1.4 First-Time Anthropic Users

If this is your first time using Anthropic models, you may see a prompt to:
1. **Describe your use case**: "Healthcare symptom screening for rural India"
2. **Accept terms**: Review and accept Anthropic's terms of service
3. **Submit**: The approval is usually instant

**Note**: This only happens once per AWS account.

---

## 🔑 Step 2: Configure AWS Credentials

### Option A: Using AWS CLI (Recommended)

1. **Install AWS CLI** (if not already installed):
   - Download from: https://aws.amazon.com/cli/
   - Or use: `pip install awscli`

2. **Configure credentials**:
   ```bash
   aws configure
   ```

3. **Enter your credentials**:
   ```
   AWS Access Key ID: YOUR_ACCESS_KEY
   AWS Secret Access Key: YOUR_SECRET_KEY
   Default region name: us-east-1
   Default output format: json
   ```

### Option B: Using Environment Variables

Create a `.env` file in your project root:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
USE_MOCK_BEDROCK=false
```

### Option C: Using IAM Role (For EC2 Deployment)

If deploying on EC2, attach an IAM role with Bedrock permissions (see Step 3).

---

## 🔐 Step 3: Create IAM Policy and Role

### 3.1 Create IAM Policy

1. Go to **IAM Console** → **Policies** → **Create Policy**
2. Click **JSON** tab
3. Paste the policy from `iam-policy-example.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockModelAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:*:*:model/amazon.titan-text-express-v1"
      ]
    },
    {
      "Sid": "BedrockListModels",
      "Effect": "Allow",
      "Action": [
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": "*"
    }
  ]
}
```

4. Name it: `SwasthyaAI-Bedrock-Policy`
5. Click **Create policy**

### 3.2 Create IAM User (For Local Development)

1. Go to **IAM Console** → **Users** → **Create user**
2. Username: `swasthyaai-bedrock-user`
3. Attach the policy: `SwasthyaAI-Bedrock-Policy`
4. Create **Access Keys** for programmatic access
5. Save the **Access Key ID** and **Secret Access Key**

### 3.3 Create IAM Role (For EC2 Deployment)

1. Go to **IAM Console** → **Roles** → **Create role**
2. Select **AWS service** → **EC2**
3. Attach the policy: `SwasthyaAI-Bedrock-Policy`
4. Name it: `SwasthyaAI-EC2-Bedrock-Role`
5. Attach this role to your EC2 instance

---

## ⚙️ Step 4: Configure SwasthyaAI Lite

### 4.1 Update Environment Variables

Edit your `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
USE_MOCK_BEDROCK=false  # ← Change this to false!

# Model Paths (keep as is)
MODEL_PATH=models/best_model.joblib
FEATURE_COLUMNS_PATH=models/feature_columns.joblib
LABEL_ENCODER_PATH=models/label_encoder.joblib
DATASET_PATH=data/disease_symptom_dataset.csv

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
UI_PORT=8501
```

### 4.2 Update Startup Scripts

**For Windows (start_backend.py):**

```python
import os
import sys

# Set environment variables
os.environ["USE_MOCK_BEDROCK"] = "false"  # ← Change to false
os.environ["AWS_REGION"] = "us-east-1"
os.environ["BEDROCK_MODEL_ID"] = "anthropic.claude-3-haiku-20240307-v1:0"

# Load from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

# Start uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
```

---

## 🧪 Step 5: Test Bedrock Integration

### 5.1 Test AWS Credentials

```bash
python -c "import boto3; client = boto3.client('bedrock', region_name='us-east-1'); print('✓ AWS credentials working')"
```

### 5.2 Test Bedrock Access

```bash
python -c "import boto3; client = boto3.client('bedrock-runtime', region_name='us-east-1'); print('✓ Bedrock access working')"
```

### 5.3 Test Symptom Extraction

Create a test script `test_bedrock.py`:

```python
import os
os.environ["USE_MOCK_BEDROCK"] = "false"
os.environ["AWS_REGION"] = "us-east-1"

from app.bedrock_integration import BedrockSymptomExtractor

# Test extraction
extractor = BedrockSymptomExtractor()
symptoms = extractor.extract_symptoms("Patient has fever, headache, and body pain")

print("Extracted symptoms:", symptoms)
```

Run it:
```bash
python test_bedrock.py
```

Expected output:
```
Extracted symptoms: ['fever', 'headache', 'body pain']
```

---

## 🚀 Step 6: Start the Application with Bedrock

### 6.1 Update RUN_APP.bat

```batch
@echo off
echo ========================================
echo SwasthyaAI Lite - Starting with AWS Bedrock
echo ========================================
echo.

REM Set environment variable for REAL Bedrock
set USE_MOCK_BEDROCK=false
set AWS_REGION=us-east-1

echo [1/2] Starting FastAPI Backend with Bedrock...
echo.
start "SwasthyaAI Backend" cmd /k "python start_backend.py"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Starting Streamlit UI...
echo.
start "SwasthyaAI UI" cmd /k "python start_ui.py"

echo.
echo ========================================
echo Application Started with AWS Bedrock!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Streamlit UI: http://localhost:8501
echo.

timeout /t 8 /nobreak > nul
start http://localhost:8501

pause
```

### 6.2 Start the Application

```bash
RUN_APP.bat
```

Or manually:
```bash
# Terminal 1
python start_backend.py

# Terminal 2
python start_ui.py
```

---

## 💰 Step 7: Monitor Costs

### Bedrock Pricing (Claude 3 Haiku)

- **Input**: $0.25 per 1M tokens
- **Output**: $1.25 per 1M tokens

### Estimated Costs

For **1000 daily screenings**:
- Average input: ~50 tokens per request
- Average output: ~20 tokens per response
- Daily cost: ~$0.10 - $0.50
- Monthly cost: ~$3 - $15

### Cost Monitoring

1. Go to **AWS Cost Explorer**
2. Filter by service: **Amazon Bedrock**
3. Set up **Budget Alerts**:
   - Go to **AWS Budgets**
   - Create budget for Bedrock
   - Set alert at $10/month

---

## 🔍 Step 8: Verify Integration

### Test Cases

1. **English Input**:
   ```
   Patient has fever and headache
   ```
   Expected: `['fever', 'headache']`

2. **Hindi Input**:
   ```
   Mujhe bukhar aur sir dard hai
   ```
   Expected: `['fever', 'headache']` (translated)

3. **Mixed Language**:
   ```
   Patient ko bukhar and body pain hai
   ```
   Expected: `['fever', 'body pain']`

### Check Backend Logs

Look for:
```
INFO - BedrockSymptomExtractor initialized with model: anthropic.claude-3-haiku-20240307-v1:0
INFO - Bedrock client initialized for region: us-east-1
INFO - Successfully extracted X symptoms
```

---

## 🐛 Troubleshooting

### Error: "Could not connect to the endpoint URL"

**Solution**: Check your AWS region
```bash
export AWS_REGION=us-east-1
```

### Error: "AccessDeniedException"

**Solution**: Verify IAM permissions
```bash
aws bedrock list-foundation-models --region us-east-1
```

### Error: "ValidationException: The provided model identifier is invalid"

**Solution**: Ensure model access is enabled in Bedrock console

### Error: "ThrottlingException"

**Solution**: You're hitting rate limits. Add retry logic or reduce request frequency.

### Bedrock Not Available in Your Region

**Solution**: Use one of these regions:
- `us-east-1` (N. Virginia) - Recommended
- `us-west-2` (Oregon)
- `eu-central-1` (Frankfurt)
- `ap-southeast-1` (Singapore)

---

## 🔄 Switching Between Mock and Real Bedrock

### Use Mock (No AWS Required)
```bash
set USE_MOCK_BEDROCK=true
```

### Use Real Bedrock
```bash
set USE_MOCK_BEDROCK=false
```

---

## 📊 Comparison: Mock vs Real Bedrock

| Feature | Mock Bedrock | Real Bedrock |
|---------|-------------|--------------|
| Cost | Free | ~$3-15/month |
| Setup | None | AWS account required |
| Accuracy | Keyword matching | AI-powered |
| Multi-language | Limited | Excellent |
| Hindi Support | Basic | Native |
| Mixed Language | Basic | Excellent |

---

## ✅ Checklist

- [ ] AWS account created
- [ ] Bedrock access enabled
- [ ] Model access granted (Claude 3 Haiku)
- [ ] IAM policy created
- [ ] IAM user/role created
- [ ] AWS credentials configured
- [ ] `.env` file updated
- [ ] `USE_MOCK_BEDROCK=false` set
- [ ] Test script runs successfully
- [ ] Application starts without errors
- [ ] Symptom extraction works
- [ ] Cost monitoring set up

---

## 📞 Support

If you encounter issues:

1. Check AWS Bedrock service status
2. Verify IAM permissions
3. Review backend logs
4. Test with mock mode first
5. Check AWS CloudWatch logs

---

## 🎉 Success!

Once configured, your application will use real AI to:
- Extract symptoms from natural language
- Support Hindi, English, and mixed languages
- Handle complex medical terminology
- Provide more accurate symptom extraction

**Your SwasthyaAI Lite is now powered by AWS Bedrock!** 🚀
