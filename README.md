# SwasthyaAI Lite

AI-powered rural health screening system for ASHA workers in India.

## 🎯 Overview

SwasthyaAI Lite is a cloud-deployable health screening system that:
- Accepts plain-language symptom descriptions (Hindi/English/mixed)
- Uses Amazon Bedrock LLMs to extract structured symptoms
- Predicts diseases using trained ML models
- Provides risk assessment and referral guidance
- Designed for rural healthcare workers with limited technical expertise

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │  (Port 8501)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend│  (Port 8000)
└────────┬────────┘
         │
    ┌────┴────┬──────────┬────────────┐
    ▼         ▼          ▼            ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│Bedrock │ │Symptom│ │ML Model│ │Risk      │
│Extract │ │Mapper │ │Predict │ │Scoring   │
└────────┘ └──────┘ └────────┘ └──────────┘
```

## 📋 Features

- **Multi-language Support**: Hindi, English, and mixed language input
- **AI Symptom Extraction**: Amazon Bedrock LLMs extract symptoms from natural language
- **Disease Prediction**: Trained ML models predict top 3 diseases with probabilities
- **Risk Assessment**: Automatic risk classification (High/Medium/Low)
- **Referral Guidance**: Context-aware recommendations for PHC referral
- **Safety First**: No autonomous diagnosis, human-in-the-loop design

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- AWS Account with Bedrock access (optional, can use mock mode)
- 2GB RAM minimum
- 1GB disk space

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd swasthyaai-lite
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Train the ML model** (first time only)
```bash
python scripts/train_model.py
```

6. **Start the backend API**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. **Start the Streamlit UI** (in a new terminal)
```bash
streamlit run ui/app.py --server.port 8501
```

8. **Access the application**
- UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t swasthyaai-lite:latest .
```

### Run Container

```bash
docker run -p 8000:8000 -p 8501:8501 \
  -e USE_MOCK_BEDROCK=true \
  swasthyaai-lite:latest
```

### With AWS Credentials

```bash
docker run -p 8000:8000 -p 8501:8501 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e USE_MOCK_BEDROCK=false \
  swasthyaai-lite:latest
```

## ☁️ AWS EC2 Deployment

### 1. Launch EC2 Instance

- **Instance Type**: t3.medium or larger
- **AMI**: Amazon Linux 2 or Ubuntu 20.04
- **Storage**: 20GB EBS volume
- **Security Group**: Open ports 8000, 8501, 22

### 2. Install Docker

```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -a -G docker ubuntu
```

### 3. Deploy Application

```bash
# Copy files to EC2
scp -r . ec2-user@<instance-ip>:~/swasthyaai-lite

# SSH into instance
ssh ec2-user@<instance-ip>

# Build and run
cd swasthyaai-lite
docker build -t swasthyaai-lite:latest .
docker run -d -p 8000:8000 -p 8501:8501 \
  --name swasthyaai \
  -e USE_MOCK_BEDROCK=true \
  swasthyaai-lite:latest
```

### 4. Configure IAM Role (for Bedrock)

Create an IAM role with this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*:*:model/*"
    }
  ]
}
```

Attach the role to your EC2 instance.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `BEDROCK_MODEL_ID` | Bedrock model ID | `anthropic.claude-3-haiku-20240307-v1:0` |
| `USE_MOCK_BEDROCK` | Use mock extractor (no AWS) | `false` |
| `MODEL_PATH` | Path to trained model | `models/best_model.joblib` |
| `DATASET_PATH` | Path to dataset | `data/disease_symptom_dataset.csv` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `UI_PORT` | Streamlit port | `8501` |

## 📊 Dataset

The system uses a disease-symptom dataset with:
- **4,920 samples**
- **41 unique diseases**
- **131 unique symptoms**

Dataset location: `data/disease_symptom_dataset.csv`

## 🧪 Testing

### Run Validation Scripts

```bash
# Data loader
python validate_data_loader.py

# Preprocessor
python validate_preprocessor.py

# ML pipeline
python validate_ml_pipeline.py

# Symptom mapper
python validate_symptom_mapper.py

# Risk engine
python validate_risk_engine.py

# Bedrock integration
python validate_bedrock_integration.py
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Analyze symptoms
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text_input": "Patient has fever and headache"}'
```

## 📁 Project Structure

```
swasthyaai-lite/
├── app/                      # Backend application
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── bedrock_integration.py
│   ├── symptom_mapper.py
│   ├── ml_predictor.py
│   ├── risk_engine.py
│   ├── data_loader.py
│   └── data_preprocessor.py
├── ui/                       # Streamlit UI
│   └── app.py
├── scripts/                  # Utility scripts
│   └── train_model.py
├── data/                     # Dataset
│   └── disease_symptom_dataset.csv
├── models/                   # Trained models
│   ├── best_model.joblib
│   ├── feature_columns.joblib
│   └── label_encoder.joblib
├── tests/                    # Test files
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## 🔒 Security Considerations

- **No PII Storage**: System does not persist patient data without consent
- **Prompt Guardrails**: LLM configured to extract symptoms only, no diagnosis
- **Input Validation**: All inputs validated before processing
- **Error Handling**: Graceful degradation on component failures
- **Audit Logging**: All predictions logged with timestamps

## 💰 Cost Estimation (AWS)

### Monthly Costs (Approximate)

- **EC2 t3.medium**: $30-40/month
- **Bedrock (Claude Haiku)**: $0.25 per 1M input tokens, $1.25 per 1M output tokens
  - Estimated: $5-20/month for 1000 daily screenings
- **Data Transfer**: $5-10/month
- **Total**: ~$40-70/month

### Cost Optimization

- Use mock Bedrock for development/testing
- Use spot instances for non-production
- Enable auto-scaling for variable load

## 🐛 Troubleshooting

### Model Not Loading

```bash
# Ensure model is trained
python scripts/train_model.py

# Check model files exist
ls -la models/
```

### Bedrock Connection Issues

```bash
# Test AWS credentials
aws bedrock list-foundation-models --region us-east-1

# Use mock mode for testing
export USE_MOCK_BEDROCK=true
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # or :8501

# Kill process
kill -9 <PID>
```

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Contact system administrator

## 📄 License

This project is developed for the AI for Bharat Hackathon.

## 🙏 Acknowledgments

- AI for Bharat initiative
- ASHA workers and PHC staff
- Rural healthcare community

## 🔄 Version History

- **v1.0.0** (2026-02-28): Initial release
  - Multi-language symptom extraction
  - Disease prediction with 3 ML models
  - Risk assessment and referral guidance
  - Docker deployment support
  - AWS Bedrock integration

---

**Built with ❤️ for rural healthcare in India**
