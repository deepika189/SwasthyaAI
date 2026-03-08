"""
Validation script for ML predictor.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml_predictor import MLPredictor, ModelLoadError, PredictionResult


def test_model_loading():
    """Test model loading."""
    print("Testing model loading...")
    
    try:
        predictor = MLPredictor()
        print(f"  ✓ Model loaded successfully")
        print(f"  ✓ Features: {len(predictor.get_feature_columns())}")
        print(f"  ✓ Disease classes: {len(predictor.get_disease_classes())}")
        return predictor
    except ModelLoadError as e:
        print(f"  ❌ Model loading failed: {e}")
        raise


def test_prediction(predictor):
    """Test prediction with sample symptoms."""
    print("\nTesting prediction...")
    
    # Test with some common symptoms
    test_symptoms = ["high_fever", "headache", "chills"]
    
    predictions = predictor.predict(test_symptoms, top_k=3)
    
    assert len(predictions) == 3, "Should return 3 predictions"
    assert all(isinstance(p, PredictionResult) for p in predictions), "All predictions should be PredictionResult"
    assert all(0 <= p.probability <= 1 for p in predictions), "Probabilities must be between 0 and 1"
    
    print(f"  ✓ Predicted {len(predictions)} diseases")
    print(f"  ✓ Input symptoms: {test_symptoms}")
    print(f"  ✓ Top predictions:")
    for i, pred in enumerate(predictions, 1):
        print(f"    {i}. {pred.disease}: {pred.probability:.4f}")


def test_empty_symptoms(predictor):
    """Test prediction with empty symptom list."""
    print("\nTesting with empty symptoms...")
    
    predictions = predictor.predict([], top_k=3)
    
    assert len(predictions) == 3, "Should still return 3 predictions"
    print(f"  ✓ Handled empty symptom list")
    print(f"  ✓ Top predictions:")
    for i, pred in enumerate(predictions, 1):
        print(f"    {i}. {pred.disease}: {pred.probability:.4f}")


def test_feature_vector_creation(predictor):
    """Test feature vector creation."""
    print("\nTesting feature vector creation...")
    
    symptoms = ["itching", "skin_rash"]
    feature_vector = predictor._create_feature_vector(symptoms)
    
    assert feature_vector.shape == (1, len(predictor.get_feature_columns())), "Feature vector shape mismatch"
    assert set(feature_vector.flatten()).issubset({0, 1}), "Feature vector must be binary"
    
    print(f"  ✓ Feature vector shape: {feature_vector.shape}")
    print(f"  ✓ Non-zero features: {feature_vector.sum()}")


def test_invalid_symptoms(predictor):
    """Test prediction with invalid symptoms."""
    print("\nTesting with invalid symptoms...")
    
    # Mix of valid and invalid symptoms
    symptoms = ["high_fever", "invalid_symptom_xyz", "headache"]
    predictions = predictor.predict(symptoms, top_k=3)
    
    assert len(predictions) == 3, "Should return 3 predictions even with invalid symptoms"
    print(f"  ✓ Handled invalid symptoms gracefully")


def test_to_dict(predictor):
    """Test PredictionResult to_dict conversion."""
    print("\nTesting PredictionResult to_dict...")
    
    predictions = predictor.predict(["high_fever"], top_k=1)
    result_dict = predictions[0].to_dict()
    
    assert "disease" in result_dict, "Dict must have 'disease' key"
    assert "probability" in result_dict, "Dict must have 'probability' key"
    assert isinstance(result_dict["disease"], str), "Disease must be string"
    assert isinstance(result_dict["probability"], float), "Probability must be float"
    
    print(f"  ✓ to_dict conversion works")
    print(f"  ✓ Result: {result_dict}")


if __name__ == "__main__":
    print("=" * 60)
    print("ML PREDICTOR VALIDATION")
    print("=" * 60)
    
    try:
        predictor = test_model_loading()
        test_prediction(predictor)
        test_empty_symptoms(predictor)
        test_feature_vector_creation(predictor)
        test_invalid_symptoms(predictor)
        test_to_dict(predictor)
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
