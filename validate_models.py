"""
Validation script for Pydantic models.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.models import (
    AnalysisRequest,
    PredictionResult,
    AnalysisResponse,
    ErrorResponse,
    HealthResponse
)
from pydantic import ValidationError


def test_analysis_request_valid():
    """Test valid AnalysisRequest."""
    print("Testing valid AnalysisRequest...")
    
    # Test with all fields
    request1 = AnalysisRequest(
        text_input="Patient has fever and headache",
        temperature=101.5,
        spo2=96,
        age=35,
        gender="female"
    )
    
    assert request1.text_input == "Patient has fever and headache"
    assert request1.temperature == 101.5
    assert request1.gender == "female"
    
    print(f"  ✓ Full request validated")
    
    # Test with only required field
    request2 = AnalysisRequest(
        text_input="Mujhe bukhar hai"
    )
    
    assert request2.text_input == "Mujhe bukhar hai"
    assert request2.temperature is None
    assert request2.age is None
    
    print(f"  ✓ Minimal request validated")


def test_analysis_request_invalid():
    """Test invalid AnalysisRequest."""
    print("\nTesting invalid AnalysisRequest...")
    
    # Empty text
    try:
        AnalysisRequest(text_input="")
        assert False, "Should raise validation error for empty text"
    except ValidationError:
        print(f"  ✓ Empty text rejected")
    
    # Text too long
    try:
        AnalysisRequest(text_input="a" * 1001)
        assert False, "Should raise validation error for text too long"
    except ValidationError:
        print(f"  ✓ Text too long rejected")
    
    # Invalid temperature
    try:
        AnalysisRequest(text_input="fever", temperature=150.0)
        assert False, "Should raise validation error for invalid temperature"
    except ValidationError:
        print(f"  ✓ Invalid temperature rejected")
    
    # Invalid spo2
    try:
        AnalysisRequest(text_input="fever", spo2=150)
        assert False, "Should raise validation error for invalid spo2"
    except ValidationError:
        print(f"  ✓ Invalid spo2 rejected")
    
    # Invalid age
    try:
        AnalysisRequest(text_input="fever", age=-5)
        assert False, "Should raise validation error for negative age"
    except ValidationError:
        print(f"  ✓ Negative age rejected")
    
    # Invalid gender
    try:
        AnalysisRequest(text_input="fever", gender="invalid")
        assert False, "Should raise validation error for invalid gender"
    except ValidationError:
        print(f"  ✓ Invalid gender rejected")


def test_prediction_result():
    """Test PredictionResult model."""
    print("\nTesting PredictionResult...")
    
    # Valid prediction
    pred = PredictionResult(disease="Malaria", probability=0.78)
    assert pred.disease == "Malaria"
    assert pred.probability == 0.78
    
    print(f"  ✓ Valid prediction created")
    
    # Invalid probability
    try:
        PredictionResult(disease="Malaria", probability=1.5)
        assert False, "Should raise validation error for probability > 1"
    except ValidationError:
        print(f"  ✓ Invalid probability rejected")


def test_analysis_response():
    """Test AnalysisResponse model."""
    print("\nTesting AnalysisResponse...")
    
    response = AnalysisResponse(
        extracted_symptoms=["fever", "headache"],
        mapped_symptoms=["high_fever", "headache"],
        top_predictions=[
            PredictionResult(disease="Malaria", probability=0.78),
            PredictionResult(disease="Typhoid", probability=0.65),
            PredictionResult(disease="Dengue", probability=0.52)
        ],
        risk_level="High",
        confidence_level="Medium",
        referral_recommendation="Immediate PHC referral required"
    )
    
    assert len(response.top_predictions) == 3
    assert response.risk_level == "High"
    assert response.confidence_level == "Medium"
    
    print(f"  ✓ Valid response created")
    print(f"  ✓ {len(response.top_predictions)} predictions")
    
    # Invalid risk level
    try:
        AnalysisResponse(
            extracted_symptoms=[],
            mapped_symptoms=[],
            top_predictions=[PredictionResult(disease="Test", probability=0.5)],
            risk_level="Invalid",
            confidence_level="Medium",
            referral_recommendation="Test"
        )
        assert False, "Should raise validation error for invalid risk level"
    except ValidationError:
        print(f"  ✓ Invalid risk level rejected")


def test_error_response():
    """Test ErrorResponse model."""
    print("\nTesting ErrorResponse...")
    
    error = ErrorResponse(
        error="Invalid input",
        detail="Text input cannot be empty"
    )
    
    assert error.error == "Invalid input"
    assert error.detail == "Text input cannot be empty"
    
    print(f"  ✓ Error response created")
    
    # Without detail
    error2 = ErrorResponse(error="Service unavailable")
    assert error2.detail is None
    
    print(f"  ✓ Error response without detail created")


def test_health_response():
    """Test HealthResponse model."""
    print("\nTesting HealthResponse...")
    
    health = HealthResponse(
        status="healthy",
        model_loaded=True,
        version="1.0.0"
    )
    
    assert health.status == "healthy"
    assert health.model_loaded is True
    assert health.version == "1.0.0"
    
    print(f"  ✓ Health response created")


def test_json_serialization():
    """Test JSON serialization."""
    print("\nTesting JSON serialization...")
    
    request = AnalysisRequest(
        text_input="Test symptoms",
        temperature=100.0
    )
    
    json_data = request.model_dump()
    assert isinstance(json_data, dict)
    assert json_data["text_input"] == "Test symptoms"
    
    print(f"  ✓ Request serialization works")
    
    response = AnalysisResponse(
        extracted_symptoms=["fever"],
        mapped_symptoms=["high_fever"],
        top_predictions=[PredictionResult(disease="Test", probability=0.5)],
        risk_level="Medium",
        confidence_level="Low",
        referral_recommendation="Test"
    )
    
    json_data = response.model_dump()
    assert isinstance(json_data, dict)
    assert "top_predictions" in json_data
    
    print(f"  ✓ Response serialization works")


if __name__ == "__main__":
    print("=" * 60)
    print("PYDANTIC MODELS VALIDATION")
    print("=" * 60)
    
    try:
        test_analysis_request_valid()
        test_analysis_request_invalid()
        test_prediction_result()
        test_analysis_response()
        test_error_response()
        test_health_response()
        test_json_serialization()
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
