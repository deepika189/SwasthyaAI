"""
Pydantic models for FastAPI request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class AnalysisRequest(BaseModel):
    """Request model for symptom analysis."""
    
    text_input: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Plain-language symptom description",
        examples=["Patient has fever and headache for 3 days"]
    )
    
    temperature: Optional[float] = Field(
        None,
        ge=95.0,
        le=110.0,
        description="Body temperature in Fahrenheit"
    )
    
    spo2: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Blood oxygen saturation percentage"
    )
    
    age: Optional[int] = Field(
        None,
        ge=0,
        le=120,
        description="Patient age in years"
    )
    
    gender: Optional[str] = Field(
        None,
        description="Patient gender",
        pattern="^(male|female|other)$"
    )
    
    @field_validator('text_input')
    @classmethod
    def validate_text_input(cls, v: str) -> str:
        """Validate text input is not empty after stripping."""
        if not v.strip():
            raise ValueError("Text input cannot be empty or whitespace only")
        return v.strip()
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize gender."""
        if v is None:
            return None
        return v.lower()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text_input": "Mujhe bukhar hai aur sir dard ho raha hai",
                    "temperature": 101.5,
                    "spo2": 96,
                    "age": 35,
                    "gender": "female"
                },
                {
                    "text_input": "Patient has cough, fatigue, and body pain",
                    "temperature": 99.8,
                    "age": 45,
                    "gender": "male"
                },
                {
                    "text_input": "Itching and skin rash for 2 days"
                }
            ]
        }
    }


class PredictionResult(BaseModel):
    """Model for a single disease prediction."""
    
    disease: str = Field(
        ...,
        description="Disease name"
    )
    
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Prediction probability (0-1)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "disease": "Malaria",
                    "probability": 0.78
                }
            ]
        }
    }


class AnalysisResponse(BaseModel):
    """Response model for symptom analysis."""
    
    extracted_symptoms: List[str] = Field(
        ...,
        description="Symptoms extracted from text input by LLM"
    )
    
    mapped_symptoms: List[str] = Field(
        ...,
        description="Symptoms mapped to valid dataset features"
    )
    
    top_predictions: List[PredictionResult] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Top 3 disease predictions with probabilities"
    )
    
    risk_level: str = Field(
        ...,
        description="Risk level: Low, Medium, or High",
        pattern="^(Low|Medium|High)$"
    )
    
    confidence_level: str = Field(
        ...,
        description="Confidence level: Low, Medium, or High",
        pattern="^(Low|Medium|High)$"
    )
    
    referral_recommendation: str = Field(
        ...,
        description="Referral recommendation based on risk level"
    )
    
    ayurvedic_remedies: Optional[str] = Field(
        None,
        description="Ayurvedic home remedy recommendations from RAG system"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "extracted_symptoms": ["fever", "headache", "body pain"],
                    "mapped_symptoms": ["high_fever", "headache", "muscle_pain"],
                    "top_predictions": [
                        {"disease": "Malaria", "probability": 0.78},
                        {"disease": "Typhoid", "probability": 0.65},
                        {"disease": "Dengue", "probability": 0.52}
                    ],
                    "risk_level": "High",
                    "confidence_level": "Medium",
                    "referral_recommendation": "Immediate PHC referral required",
                    "ayurvedic_remedies": "1. Drink ginger tea with honey\n2. Get adequate rest\n3. Stay hydrated"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(
        ...,
        description="Error message"
    )
    
    detail: Optional[str] = Field(
        None,
        description="Detailed error information"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Invalid input",
                    "detail": "Text input cannot be empty"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(
        ...,
        description="Service status"
    )
    
    model_loaded: bool = Field(
        ...,
        description="Whether ML model is loaded"
    )
    
    version: str = Field(
        default="1.0.0",
        description="API version"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "model_loaded": True,
                    "version": "1.0.0"
                }
            ]
        }
    }
