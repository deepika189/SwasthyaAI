"""
Validation script for risk scoring engine.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.risk_engine import RiskScoringEngine
from app.ml_predictor import PredictionResult


def test_initialization():
    """Test risk engine initialization."""
    print("Testing risk engine initialization...")
    
    engine = RiskScoringEngine()
    assert engine.high_risk_threshold == 0.70
    assert engine.medium_risk_threshold == 0.40
    
    print(f"  ✓ Engine initialized")
    print(f"  ✓ High risk threshold: {engine.high_risk_threshold}")
    print(f"  ✓ Medium risk threshold: {engine.medium_risk_threshold}")
    
    return engine


def test_risk_classification(engine):
    """Test risk level classification."""
    print("\nTesting risk level classification...")
    
    test_cases = [
        (0.75, "High"),
        (0.70, "High"),
        (0.69, "Medium"),
        (0.50, "Medium"),
        (0.40, "Medium"),
        (0.39, "Low"),
        (0.20, "Low"),
        (0.00, "Low"),
    ]
    
    for probability, expected_risk in test_cases:
        predictions = [PredictionResult("Test Disease", probability)]
        risk, _, _ = engine.calculate_risk(predictions, num_symptoms=3)
        
        assert risk == expected_risk, f"Expected {expected_risk}, got {risk} for probability {probability}"
        print(f"  ✓ Probability {probability:.2f} → Risk: {risk}")


def test_confidence_calculation(engine):
    """Test confidence level calculation."""
    print("\nTesting confidence level calculation...")
    
    test_cases = [
        (0, "Low"),
        (1, "Low"),
        (2, "Medium"),
        (3, "Medium"),
        (4, "High"),
        (5, "High"),
        (10, "High"),
    ]
    
    predictions = [PredictionResult("Test Disease", 0.5)]
    
    for num_symptoms, expected_confidence in test_cases:
        _, confidence, _ = engine.calculate_risk(predictions, num_symptoms)
        
        assert confidence == expected_confidence, f"Expected {expected_confidence}, got {confidence} for {num_symptoms} symptoms"
        print(f"  ✓ {num_symptoms} symptoms → Confidence: {confidence}")


def test_referral_mapping(engine):
    """Test referral recommendation mapping."""
    print("\nTesting referral recommendation mapping...")
    
    test_cases = [
        ("High", "Immediate PHC referral required"),
        ("Medium", "Visit PHC within 24 hours"),
        ("Low", "Home care monitoring recommended"),
    ]
    
    for risk_level, expected_referral in test_cases:
        referral = engine._generate_referral(risk_level)
        
        assert referral == expected_referral, f"Expected '{expected_referral}', got '{referral}'"
        print(f"  ✓ {risk_level} risk → {referral}")


def test_boundary_values(engine):
    """Test boundary values for risk classification."""
    print("\nTesting boundary values...")
    
    # Test exact boundary values
    boundary_tests = [
        (0.70, "High", "Boundary: 0.70 should be High"),
        (0.6999, "Medium", "Just below high threshold"),
        (0.40, "Medium", "Boundary: 0.40 should be Medium"),
        (0.3999, "Low", "Just below medium threshold"),
    ]
    
    for probability, expected_risk, description in boundary_tests:
        predictions = [PredictionResult("Test Disease", probability)]
        risk, _, _ = engine.calculate_risk(predictions, num_symptoms=3)
        
        assert risk == expected_risk, f"{description}: Expected {expected_risk}, got {risk}"
        print(f"  ✓ {description}: {probability:.4f} → {risk}")


def test_empty_predictions(engine):
    """Test with empty predictions list."""
    print("\nTesting empty predictions...")
    
    risk, confidence, referral = engine.calculate_risk([], num_symptoms=2)
    
    assert risk == "Low", "Empty predictions should result in Low risk"
    assert confidence == "Medium", "2 symptoms should give Medium confidence"
    
    print(f"  ✓ Empty predictions handled")
    print(f"  ✓ Risk: {risk}, Confidence: {confidence}")


def test_combined_scenarios(engine):
    """Test combined risk and confidence scenarios."""
    print("\nTesting combined scenarios...")
    
    scenarios = [
        {
            "name": "High risk, High confidence",
            "probability": 0.85,
            "num_symptoms": 5,
            "expected_risk": "High",
            "expected_confidence": "High",
            "expected_referral": "Immediate PHC referral required"
        },
        {
            "name": "High risk, Low confidence",
            "probability": 0.75,
            "num_symptoms": 1,
            "expected_risk": "High",
            "expected_confidence": "Low",
            "expected_referral": "Immediate PHC referral required"
        },
        {
            "name": "Medium risk, Medium confidence",
            "probability": 0.55,
            "num_symptoms": 3,
            "expected_risk": "Medium",
            "expected_confidence": "Medium",
            "expected_referral": "Visit PHC within 24 hours"
        },
        {
            "name": "Low risk, High confidence",
            "probability": 0.25,
            "num_symptoms": 6,
            "expected_risk": "Low",
            "expected_confidence": "High",
            "expected_referral": "Home care monitoring recommended"
        },
    ]
    
    for scenario in scenarios:
        predictions = [PredictionResult("Test Disease", scenario["probability"])]
        risk, confidence, referral = engine.calculate_risk(predictions, scenario["num_symptoms"])
        
        assert risk == scenario["expected_risk"], f"Risk mismatch in {scenario['name']}"
        assert confidence == scenario["expected_confidence"], f"Confidence mismatch in {scenario['name']}"
        assert referral == scenario["expected_referral"], f"Referral mismatch in {scenario['name']}"
        
        print(f"  ✓ {scenario['name']}")
        print(f"    Risk: {risk}, Confidence: {confidence}")


def test_threshold_adjustment(engine):
    """Test custom threshold adjustment."""
    print("\nTesting threshold adjustment...")
    
    # Set custom thresholds
    engine.set_thresholds(high_threshold=0.80, medium_threshold=0.50)
    
    predictions = [PredictionResult("Test Disease", 0.75)]
    risk, _, _ = engine.calculate_risk(predictions, num_symptoms=3)
    
    assert risk == "Medium", "With new thresholds, 0.75 should be Medium"
    print(f"  ✓ Custom thresholds applied")
    print(f"  ✓ Probability 0.75 → Risk: {risk} (with high=0.80, medium=0.50)")
    
    # Reset to defaults
    engine.set_thresholds(high_threshold=0.70, medium_threshold=0.40)


if __name__ == "__main__":
    print("=" * 60)
    print("RISK SCORING ENGINE VALIDATION")
    print("=" * 60)
    
    try:
        engine = test_initialization()
        test_risk_classification(engine)
        test_confidence_calculation(engine)
        test_referral_mapping(engine)
        test_boundary_values(engine)
        test_empty_predictions(engine)
        test_combined_scenarios(engine)
        test_threshold_adjustment(engine)
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
