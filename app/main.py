"""
FastAPI application for SwasthyaAI Lite.
Main backend API service orchestrating all components.
"""

import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import models
from app.models import (
    AnalysisRequest,
    AnalysisResponse,
    PredictionResult,
    ErrorResponse,
    HealthResponse
)

# Import components
from app.bedrock_integration import BedrockSymptomExtractor, MockBedrockSymptomExtractor
from app.symptom_mapper import SymptomMapper
from app.ml_predictor import MLPredictor, ModelLoadError
from app.risk_engine import RiskScoringEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global components (initialized on startup)
bedrock_extractor: Optional[BedrockSymptomExtractor] = None
symptom_mapper: Optional[SymptomMapper] = None
ml_predictor: Optional[MLPredictor] = None
risk_engine: Optional[RiskScoringEngine] = None
rag_system = None  # RAG system for Ayurvedic remedies
model_loaded: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("=" * 60)
    logger.info("SWASTHYAAI LITE API STARTING")
    logger.info("=" * 60)
    
    global bedrock_extractor, symptom_mapper, ml_predictor, risk_engine, rag_system, model_loaded
    
    try:
        # Load environment variables
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
        model_path = os.getenv("MODEL_PATH", "models/best_model.joblib")
        dataset_path = os.getenv("DATASET_PATH", "data/disease_symptom_dataset.csv")
        use_mock_bedrock = os.getenv("USE_MOCK_BEDROCK", "false").lower() == "true"
        
        # RAG configuration
        rag_enabled = os.getenv("RAG_ENABLED", "true").lower() == "true"
        rag_pdf_path = os.getenv("RAG_PDF_PATH", "data/The complete book of Ayurvedic home remedies.pdf")
        rag_index_path = os.getenv("RAG_INDEX_PATH", "data/faiss_index")
        rag_max_chunks = int(os.getenv("RAG_MAX_CHUNKS", "100"))
        
        logger.info(f"AWS Region: {aws_region}")
        logger.info(f"Bedrock Model: {bedrock_model_id}")
        logger.info(f"Model Path: {model_path}")
        logger.info(f"Use Mock Bedrock: {use_mock_bedrock}")
        logger.info(f"RAG Enabled: {rag_enabled}")
        
        # Initialize Bedrock extractor
        if use_mock_bedrock:
            logger.info("Initializing Mock Bedrock extractor...")
            bedrock_extractor = MockBedrockSymptomExtractor()
        else:
            logger.info("Initializing Bedrock extractor...")
            bedrock_extractor = BedrockSymptomExtractor(
                model_id=bedrock_model_id,
                region=aws_region
            )
        
        # Initialize symptom mapper
        logger.info("Initializing symptom mapper...")
        symptom_mapper = SymptomMapper(dataset_path=dataset_path)
        
        # Initialize ML predictor
        logger.info("Initializing ML predictor...")
        ml_predictor = MLPredictor(model_path=model_path)
        model_loaded = True
        
        # Initialize risk engine
        logger.info("Initializing risk scoring engine...")
        risk_engine = RiskScoringEngine()
        
        # Initialize RAG system (non-blocking)
        if rag_enabled:
            try:
                logger.info("Initializing Ayurvedic RAG system...")
                from app.rag_system import AyurvedicRAGSystem
                
                rag_system = AyurvedicRAGSystem(
                    pdf_path=rag_pdf_path,
                    region=aws_region,
                    index_path=rag_index_path,
                    max_chunks=rag_max_chunks
                )
                rag_system.initialize()
                logger.info("RAG system initialized ✓")
            except Exception as e:
                logger.error(f"RAG initialization failed: {e}")
                logger.warning("API will continue without RAG functionality")
                rag_system = None
        else:
            logger.info("RAG system disabled by configuration")
            rag_system = None
        
        logger.info("=" * 60)
        logger.info("ALL COMPONENTS INITIALIZED SUCCESSFULLY ✓")
        logger.info("=" * 60)
        
    except ModelLoadError as e:
        logger.error(f"Failed to load ML model: {e}")
        logger.error("API will start but /analyze endpoint will not work")
        model_loaded = False
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SwasthyaAI Lite API...")


# Create FastAPI app
app = FastAPI(
    title="SwasthyaAI Lite API",
    description="AI-powered rural health screening system for ASHA workers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "SwasthyaAI Lite API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and model loading state.
    """
    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        version="1.0.0"
    )


@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    tags=["Analysis"]
)
async def analyze_symptoms(request: AnalysisRequest):
    """
    Analyze patient symptoms and provide disease predictions with risk assessment.
    
    This endpoint:
    1. Extracts symptoms from plain-language input using LLM
    2. Maps extracted symptoms to valid dataset features
    3. Predicts top 3 diseases using trained ML model
    4. Calculates risk level and confidence
    5. Generates referral recommendation
    
    Args:
        request: AnalysisRequest containing symptom description and optional vitals
        
    Returns:
        AnalysisResponse with predictions, risk assessment, and referral guidance
    """
    try:
        # Check if model is loaded
        if not model_loaded or ml_predictor is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML model not loaded. Please ensure model training is complete."
            )
        
        logger.info(f"Analyzing symptoms: '{request.text_input[:50]}...'")
        
        # Step 1: Extract symptoms using Bedrock
        logger.info("Step 1: Extracting symptoms...")
        try:
            extracted_symptoms = bedrock_extractor.extract_symptoms(request.text_input)
            logger.info(f"Extracted {len(extracted_symptoms)} symptoms: {extracted_symptoms}")
        except Exception as e:
            logger.error(f"Symptom extraction failed: {e}")
            # Continue with empty symptoms rather than failing
            extracted_symptoms = []
        
        # Step 2: Map symptoms to valid features
        logger.info("Step 2: Mapping symptoms...")
        mapped_symptoms = symptom_mapper.map_symptoms(extracted_symptoms)
        logger.info(f"Mapped {len(mapped_symptoms)} symptoms: {mapped_symptoms}")
        
        # Step 3: Predict diseases
        logger.info("Step 3: Predicting diseases...")
        predictions = ml_predictor.predict(mapped_symptoms, top_k=3)
        logger.info(f"Generated {len(predictions)} predictions")
        
        # Convert to response format
        top_predictions = [
            PredictionResult(disease=pred.disease, probability=pred.probability)
            for pred in predictions
        ]
        
        # Step 4: Calculate risk and confidence
        logger.info("Step 4: Calculating risk...")
        risk_level, confidence_level, referral_recommendation = risk_engine.calculate_risk(
            predictions,
            num_symptoms=len(mapped_symptoms)
        )
        
        logger.info(f"Risk: {risk_level}, Confidence: {confidence_level}")
        
        # Step 5: Get Ayurvedic remedies (non-blocking)
        ayurvedic_remedies = None
        if rag_system is not None:
            try:
                logger.info("Step 5: Retrieving Ayurvedic remedies...")
                ayurvedic_remedies = rag_system.get_remedies(request.text_input)
                logger.info("Ayurvedic remedies retrieved ✓")
            except Exception as e:
                logger.error(f"RAG query failed: {e}")
                ayurvedic_remedies = "Ayurvedic remedies temporarily unavailable."
        
        # Step 6: Log prediction
        log_prediction(request, extracted_symptoms, mapped_symptoms, top_predictions, risk_level)
        
        # Build response
        response = AnalysisResponse(
            extracted_symptoms=extracted_symptoms,
            mapped_symptoms=mapped_symptoms,
            top_predictions=top_predictions,
            risk_level=risk_level,
            confidence_level=confidence_level,
            referral_recommendation=referral_recommendation,
            ayurvedic_remedies=ayurvedic_remedies
        )
        
        logger.info("Analysis complete ✓")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


def log_prediction(
    request: AnalysisRequest,
    extracted_symptoms: list,
    mapped_symptoms: list,
    predictions: list,
    risk_level: str
):
    """
    Log prediction for audit purposes.
    
    Args:
        request: Original request
        extracted_symptoms: Extracted symptoms
        mapped_symptoms: Mapped symptoms
        predictions: Prediction results
        risk_level: Risk level
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "input": request.text_input,
        "extracted_symptoms": extracted_symptoms,
        "mapped_symptoms": mapped_symptoms,
        "top_prediction": predictions[0].disease if predictions else None,
        "risk_level": risk_level,
        "vitals": {
            "temperature": request.temperature,
            "spo2": request.spo2,
            "age": request.age,
            "gender": request.gender
        }
    }
    
    # Log to file or database
    logger.info(f"PREDICTION_LOG: {log_entry}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
