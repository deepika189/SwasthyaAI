# SwasthyaAI Lite - Complete System Flowchart

## 🚀 System Startup Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION STARTUP                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌───────────────┐                      ┌───────────────┐
│  Backend API  │                      │  Streamlit UI │
│  (Port 8000)  │                      │  (Port 8501)  │
└───────────────┘                      └───────────────┘
        ↓                                       ↓
┌───────────────────────────────────┐   ┌──────────────┐
│  BACKEND INITIALIZATION           │   │  UI Renders  │
│  (app/main.py - lifespan)         │   │  Main Page   │
└───────────────────────────────────┘   └──────────────┘
        ↓
┌───────────────────────────────────────────────────────┐
│  Step 1: Load Environment Variables                   │
│  - AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_KEY     │
│  - BEDROCK_MODEL_ID                                   │
│  - MODEL_PATH, DATASET_PATH                           │
│  - USE_MOCK_BEDROCK (true/false)                      │
│  - RAG_ENABLED, RAG_PDF_PATH, RAG_INDEX_PATH         │
└───────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────┐
│  Step 2: Initialize Bedrock Symptom Extractor         │
│  - If USE_MOCK_BEDROCK=true → MockBedrockExtractor   │
│  - If USE_MOCK_BEDROCK=false → BedrockExtractor      │
└───────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────┐
│  Step 3: Initialize Symptom Mapper                    │
│  - Loads disease_symptom_dataset.csv                  │
│  - Builds valid symptom list                          │
└───────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────┐
│  Step 4: Initialize ML Predictor                      │
│  - Loads trained model (best_model.joblib)            │
│  - Loads feature columns                              │
│  - Loads label encoder                                │
│  ✓ SUCCESS → model_loaded = True                      │
│  ✗ FAILURE → model_loaded = False (API still starts)  │
└───────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────┐
│  Step 5: Initialize Risk Scoring Engine               │
│  - Ready to calculate risk levels                     │
└───────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────┐
│  Step 6: Initialize RAG System (if RAG_ENABLED=true)  │
└───────────────────────────────────────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
  [YES]   [NO]
    ↓       ↓
    │   ┌───────────────────────────────┐
    │   │ rag_system = None             │
    │   │ Log: "RAG disabled"           │
    │   └───────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│  RAG Initialization (app/rag_system.py)             │
│  Try:                                               │
│    1. Create AyurvedicRAGSystem instance            │
│    2. Call rag_system.initialize()                  │
└─────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────┐
│  Check if FAISS index exists at RAG_INDEX_PATH      │
└─────────────────────────────────────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
[EXISTS] [NOT EXISTS]
    ↓       ↓
    │   ┌───────────────────────────────────────────┐
    │   │  BUILD NEW INDEX (First Time Only)        │
    │   │  1. PDFProcessor.load_and_chunk()         │
    │   │     - Extract text from PDF               │
    │   │     - Split into chunks (1000 chars)      │
    │   │     - Add metadata                         │
    │   │  2. BedrockEmbeddings.embed_documents()   │
    │   │     - Generate vectors (batch of 25)      │
    │   │     - Retry on failures                   │
    │   │  3. Create FAISS index                    │
    │   │  4. Save index to disk                    │
    │   │  ⏱️ Takes 2-3 minutes                      │
    │   └───────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│  LOAD EXISTING INDEX (Fast - seconds)               │
│  - Read from disk                                   │
│  - No PDF processing needed                         │
└─────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────┐
│  RAG Initialization Result                          │
│  ✓ SUCCESS → rag_system ready                       │
│  ✗ FAILURE → rag_system = None (API still works)    │
└─────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────┐
│  ✅ BACKEND READY - All components initialized       │
│  API listening on http://localhost:8000             │
└─────────────────────────────────────────────────────┘


## 📝 User Request Flow (Main Analysis Pipeline)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                          │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  UI: User enters symptoms in text box                       │
│  Example: "Patient has fever, headache, body pain"          │
│  Language: Hindi, English, or mixed                         │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  UI: User clicks "🔍 Analyze Symptoms" button                │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  UI Validation (ui/app.py - analyze_symptoms)               │
│  - Check if text_input is not empty                         │
│  - Show spinner: "🔄 Analyzing symptoms..."                  │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  HTTP POST Request to Backend                               │
│  URL: http://localhost:8000/analyze                         │
│  Payload: {"text_input": "Patient has fever..."}            │
│  Timeout: 30 seconds                                         │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  BACKEND: /analyze endpoint (app/main.py)                   │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  Pre-Check: Is ML model loaded?                             │
└─────────────────────────────────────────────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
  [YES]   [NO]
    ↓       ↓
    │   ┌───────────────────────────────────────────┐
    │   │  Return HTTP 503 Service Unavailable      │
    │   │  Error: "ML model not loaded"             │
    │   │  → UI shows error message                 │
    │   │  → STOP                                   │
    │   └───────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Extract Symptoms using Bedrock LLM                 │
│  (app/bedrock_integration.py)                               │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  bedrock_extractor.extract_symptoms(text_input)             │
│  - Sends text to Claude 3 Haiku (or Mock)                   │
│  - LLM extracts medical symptoms                            │
│  - Returns list: ["fever", "headache", "body pain"]         │
└─────────────────────────────────────────────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
[SUCCESS] [FAILURE]
    ↓       ↓
    │   ┌───────────────────────────────────────────┐
    │   │  Log error                                │
    │   │  extracted_symptoms = []                  │
    │   │  Continue with empty list                 │
    │   └───────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Map Symptoms to Valid Features                     │
│  (app/symptom_mapper.py)                                    │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  symptom_mapper.map_symptoms(extracted_symptoms)            │
│  - Uses fuzzy matching (difflib)                            │
│  - Maps to dataset column names                             │
│  - Example: "body pain" → "muscle_wasting"                  │
│  - Returns: ["fever", "headache", "muscle_wasting"]         │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Predict Diseases using ML Model                    │
│  (app/ml_predictor.py)                                      │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  ml_predictor.predict(mapped_symptoms, top_k=3)             │
│  1. Create feature vector (one-hot encoding)                │
│  2. Run through trained model                               │
│  3. Get probability scores                                  │
│  4. Return top 3 predictions                                │
│  Example: [                                                 │
│    {disease: "Malaria", probability: 0.85},                 │
│    {disease: "Dengue", probability: 0.72},                  │
│    {disease: "Typhoid", probability: 0.65}                  │
│  ]                                                          │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Calculate Risk Level                               │
│  (app/risk_engine.py)                                       │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  risk_engine.calculate_risk(predictions, num_symptoms)      │
│  Logic:                                                     │
│  - High Risk: top_prob > 0.7 OR num_symptoms > 5           │
│  - Medium Risk: top_prob > 0.5 OR num_symptoms > 3         │
│  - Low Risk: otherwise                                      │
│  Returns:                                                   │
│  - risk_level: "High" / "Medium" / "Low"                    │
│  - confidence_level: "High" / "Medium" / "Low"              │
│  - referral_recommendation: action message                  │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Get Ayurvedic Remedies (RAG System)                │
│  (app/rag_system.py)                                        │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  Check: Is rag_system initialized?                          │
└─────────────────────────────────────────────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
  [YES]   [NO]
    ↓       ↓
    │   ┌───────────────────────────────────────────┐
    │   │  ayurvedic_remedies = None                │
    │   │  Skip RAG, continue to Step 6             │
    │   └───────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Try: rag_system.get_remedies(text_input)                   │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  RAG PIPELINE (app/rag_system.py)                           │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  5a. Embed Query                                            │
│  - BedrockEmbeddings.embed_query(text_input)                │
│  - Converts text to 1536-dim vector                         │
│  - Uses Amazon Titan embeddings model                       │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  5b. Retrieve Context from FAISS                            │
│  - vectorstore.similarity_search(query, k=3)                │
│  - Finds top 3 most similar chunks from PDF                 │
│  - Returns relevant Ayurvedic remedy text                   │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  5c. Generate Remedies using LLM                            │
│  - RemedyGenerator.generate(query, context_chunks)          │
│  - Builds prompt with guardrails                            │
│  - Calls Claude 3 Haiku                                     │
│  - Returns formatted remedy suggestions                     │
└─────────────────────────────────────────────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
[SUCCESS] [FAILURE]
    ↓       ↓
    │   ┌───────────────────────────────────────────┐
    │   │  Log error                                │
    │   │  ayurvedic_remedies =                     │
    │   │    "Remedies temporarily unavailable"     │
    │   └───────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  ayurvedic_remedies = Generated remedy text                 │
│  Example: "For fever and headache:                          │
│  1. Drink ginger tea with honey                             │
│  2. Apply sandalwood paste on forehead                      │
│  3. Rest in cool environment..."                            │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Build Response Object                              │
│  (app/main.py)                                              │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  Create AnalysisResponse (app/models.py)                    │
│  {                                                          │
│    "extracted_symptoms": ["fever", "headache"],             │
│    "mapped_symptoms": ["fever", "headache"],                │
│    "top_predictions": [                                     │
│      {"disease": "Malaria", "probability": 0.85},           │
│      {"disease": "Dengue", "probability": 0.72},            │
│      {"disease": "Typhoid", "probability": 0.65}            │
│    ],                                                       │
│    "risk_level": "High",                                    │
│    "confidence_level": "High",                              │
│    "referral_recommendation": "Immediate PHC referral",     │
│    "ayurvedic_remedies": "For fever and headache..."        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  Log Prediction for Audit                                   │
│  - Timestamp, input, symptoms, predictions, risk            │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  Return HTTP 200 OK with JSON response                      │
│  → Sent back to UI                                          │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  UI RECEIVES RESPONSE (ui/app.py)                           │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  Check HTTP Status Code                                     │
└─────────────────────────────────────────────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
  [200]   [ERROR]
    ↓       ↓
    │   ┌───────────────────────────────────────────┐
    │   │  Display Error Message                    │
    │   │  - Connection error                       │
    │   │  - Timeout error                          │
    │   │  - API error                              │
    │   │  → STOP                                   │
    │   └───────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  UI: display_results(results)                               │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  DISPLAY SECTION 1: Extracted Symptoms                      │
│  - Show symptom badges                                      │
│  - Blue pills with symptom names                            │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  DISPLAY SECTION 2: Mapped Symptoms (Expandable)            │
│  - Technical details in expander                            │
│  - Shows dataset column names                               │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  DISPLAY SECTION 3: Top 3 Predictions                       │
│  - Disease name + probability percentage                    │
│  - Progress bar for each prediction                         │
│  - Sorted by probability (highest first)                    │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  DISPLAY SECTION 4: Risk Assessment                         │
│  - Color-coded box (Red/Yellow/Green)                       │
│  - Risk level + Confidence level                            │
│  - Referral recommendation                                  │
│  - Warning if confidence is low                             │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  DISPLAY SECTION 5: Ayurvedic Remedies (if available)       │
│  - 🌿 Section header                                         │
│  - Disclaimer box (supplementary information)               │
│  - Remedy text from RAG system                              │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  DISPLAY SECTION 6: Action Buttons                          │
│  - "🔄 Analyze Another Patient" → Refresh page               │
│  - "📄 Print Results" → Browser print dialog                 │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  ✅ COMPLETE - User sees full analysis results               │
└─────────────────────────────────────────────────────────────┘
```


## 🚨 Error Handling Flows

### Error Case 1: Backend Connection Failure
```
UI sends request → Connection Error
        ↓
UI displays: "Cannot connect to API server"
        ↓
User action: Check if backend is running
```

### Error Case 2: ML Model Not Loaded
```
Request arrives → model_loaded = False
        ↓
Return HTTP 503 Service Unavailable
        ↓
UI displays: "ML model not loaded"
        ↓
Admin action: Check model files exist
```

### Error Case 3: Symptom Extraction Fails
```
Bedrock API error → Exception caught
        ↓
extracted_symptoms = []
        ↓
Continue with empty symptoms
        ↓
ML prediction still works (with low confidence)
```

### Error Case 4: RAG System Fails
```
RAG query error → Exception caught
        ↓
ayurvedic_remedies = "Temporarily unavailable"
        ↓
ML predictions still returned
        ↓
User sees predictions without remedies
```

### Error Case 5: Request Timeout
```
Request takes > 30 seconds → Timeout
        ↓
UI displays: "Request timed out"
        ↓
User action: Try again
```

### Error Case 6: Invalid Input
```
Empty text input → Validation fails
        ↓
UI displays: "Please describe symptoms"
        ↓
User action: Enter symptoms
```


## 🔄 Component Interaction Diagram

```
┌─────────────┐
│  Streamlit  │
│     UI      │
│ (Port 8501) │
└──────┬──────┘
       │ HTTP POST /analyze
       │ {"text_input": "..."}
       ↓
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│                     (Port 8000)                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │              /analyze Endpoint                     │  │
│  └────────────────────────────────────────────────────┘  │
│         ↓              ↓              ↓              ↓    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Bedrock  │  │ Symptom  │  │    ML    │  │   Risk   │ │
│  │Extractor │  │  Mapper  │  │Predictor │  │  Engine  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│         ↓                                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │              RAG System                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │  │
│  │  │   PDF    │  │ Bedrock  │  │   Remedy     │    │  │
│  │  │Processor │  │Embeddings│  │  Generator   │    │  │
│  │  └──────────┘  └──────────┘  └──────────────┘    │  │
│  │         ↓              ↓              ↓            │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │         FAISS Vector Store                 │   │  │
│  │  │  (Persistent on disk: data/faiss_index/)   │   │  │
│  │  └────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
       │
       │ HTTP 200 OK
       │ AnalysisResponse JSON
       ↓
┌─────────────┐
│  Streamlit  │
│     UI      │
│  (Display)  │
└─────────────┘
```

## 📊 Data Flow Summary

### Input Data
- User text: "Patient has fever, headache, body pain"
- Language: Hindi/English/Mixed

### Processing Stages
1. **Symptom Extraction**: Text → ["fever", "headache", "body pain"]
2. **Symptom Mapping**: ["fever", "headache", "body pain"] → ["fever", "headache", "muscle_wasting"]
3. **ML Prediction**: Feature vector → [Malaria: 0.85, Dengue: 0.72, Typhoid: 0.65]
4. **Risk Calculation**: Predictions + Symptoms → High Risk
5. **RAG Retrieval**: Query → Top 3 PDF chunks
6. **Remedy Generation**: Chunks → Formatted remedy text

### Output Data
```json
{
  "extracted_symptoms": ["fever", "headache", "body pain"],
  "mapped_symptoms": ["fever", "headache", "muscle_wasting"],
  "top_predictions": [
    {"disease": "Malaria", "probability": 0.85},
    {"disease": "Dengue", "probability": 0.72},
    {"disease": "Typhoid", "probability": 0.65}
  ],
  "risk_level": "High",
  "confidence_level": "High",
  "referral_recommendation": "URGENT: Refer to PHC immediately",
  "ayurvedic_remedies": "For fever and headache:\n1. Ginger tea..."
}
```


## 🔐 Key Design Principles

### 1. Graceful Degradation
- If RAG fails → ML predictions still work
- If symptom extraction fails → Continue with empty symptoms
- If model not loaded → API returns clear error

### 2. Non-Blocking Initialization
- RAG initialization doesn't block API startup
- API starts even if RAG fails
- First-time PDF processing happens in background

### 3. Error Isolation
- Each component has try-except blocks
- Errors logged but don't crash the system
- User always gets a response (even if partial)

### 4. Performance Optimization
- FAISS index persisted to disk
- First run: 2-3 minutes (PDF processing)
- Subsequent runs: Seconds (load from disk)
- Batch embedding: 25 documents at a time

### 5. Retry Logic
- Bedrock API calls: 3 retries with exponential backoff
- LLM generation: 2 retries
- Graceful fallback messages on failure

## 📁 File Responsibilities

| File | Responsibility |
|------|---------------|
| `ui/app.py` | Streamlit UI, user input, display results |
| `app/main.py` | FastAPI backend, orchestration, endpoints |
| `app/bedrock_integration.py` | Symptom extraction using Claude |
| `app/symptom_mapper.py` | Fuzzy matching to dataset features |
| `app/ml_predictor.py` | Disease prediction using trained model |
| `app/risk_engine.py` | Risk level calculation |
| `app/rag_system.py` | RAG orchestration |
| `app/pdf_processor.py` | PDF text extraction and chunking |
| `app/bedrock_embeddings.py` | Vector embeddings via Titan |
| `app/remedy_generator.py` | LLM-based remedy generation |
| `app/models.py` | Pydantic data models |

## 🎯 Success Criteria

✅ User enters symptoms in any language
✅ System extracts and maps symptoms
✅ ML model predicts top 3 diseases
✅ Risk level calculated accurately
✅ Ayurvedic remedies retrieved from PDF
✅ All results displayed in user-friendly UI
✅ System works even if RAG fails
✅ Errors handled gracefully
✅ Fast response time (<5 seconds typical)

---

**End of Flowchart Documentation**
