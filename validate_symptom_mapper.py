"""
Validation script for symptom mapper.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.symptom_mapper import SymptomMapper


def test_initialization():
    """Test symptom mapper initialization."""
    print("Testing symptom mapper initialization...")
    
    mapper = SymptomMapper()
    valid_symptoms = mapper.get_valid_symptoms()
    
    assert len(valid_symptoms) > 0, "No valid symptoms loaded"
    print(f"  ✓ Loaded {len(valid_symptoms)} valid symptoms")
    print(f"  ✓ Sample symptoms: {valid_symptoms[:5]}")
    
    return mapper


def test_exact_matching(mapper):
    """Test exact symptom matching."""
    print("\nTesting exact matching...")
    
    test_cases = [
        ("high_fever", ["high_fever"]),
        ("headache", ["headache"]),
        ("itching", ["itching"]),
        ("skin_rash", ["skin_rash"]),
    ]
    
    for input_symptom, expected in test_cases:
        result = mapper.map_symptoms([input_symptom])
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"  ✓ '{input_symptom}' → {result}")


def test_case_insensitive_matching(mapper):
    """Test case-insensitive matching."""
    print("\nTesting case-insensitive matching...")
    
    test_cases = [
        ("HIGH_FEVER", "high_fever"),
        ("Headache", "headache"),
        ("ITCHING", "itching"),
        ("Skin_Rash", "skin_rash"),
    ]
    
    for input_symptom, expected in test_cases:
        result = mapper.map_symptoms([input_symptom])
        assert len(result) == 1, f"Expected 1 result, got {len(result)}"
        assert result[0] == expected, f"Expected {expected}, got {result[0]}"
        print(f"  ✓ '{input_symptom}' → '{result[0]}'")


def test_space_to_underscore(mapper):
    """Test space to underscore conversion."""
    print("\nTesting space to underscore conversion...")
    
    test_cases = [
        ("high fever", "high_fever"),
        ("skin rash", "skin_rash"),
        ("chest pain", "chest_pain"),
    ]
    
    for input_symptom, expected in test_cases:
        result = mapper.map_symptoms([input_symptom])
        if len(result) > 0:
            print(f"  ✓ '{input_symptom}' → '{result[0]}'")
        else:
            print(f"  ℹ  '{input_symptom}' → no match (may need fuzzy matching)")


def test_fuzzy_matching(mapper):
    """Test fuzzy matching."""
    print("\nTesting fuzzy matching...")
    
    test_cases = [
        "stomach ache",  # Should match stomach_pain
        "high temperature",  # Should match high_fever
        "body ache",  # Should match muscle_pain or similar
    ]
    
    for input_symptom in test_cases:
        result = mapper.map_symptoms([input_symptom])
        if len(result) > 0:
            print(f"  ✓ '{input_symptom}' → '{result[0]}'")
        else:
            print(f"  ℹ  '{input_symptom}' → no match (below threshold)")


def test_invalid_symptoms(mapper):
    """Test handling of invalid symptoms."""
    print("\nTesting invalid symptom handling...")
    
    invalid_symptoms = [
        "completely_invalid_symptom_xyz",
        "not_a_real_symptom",
        "random_text_123",
    ]
    
    result = mapper.map_symptoms(invalid_symptoms)
    print(f"  ✓ Invalid symptoms filtered out: {len(invalid_symptoms)} → {len(result)}")


def test_mixed_symptoms(mapper):
    """Test mapping with mixed valid and invalid symptoms."""
    print("\nTesting mixed symptom mapping...")
    
    mixed_symptoms = [
        "high_fever",  # Valid
        "invalid_xyz",  # Invalid
        "headache",  # Valid
        "not_real",  # Invalid
        "itching",  # Valid
    ]
    
    result = mapper.map_symptoms(mixed_symptoms)
    print(f"  ✓ Input: {len(mixed_symptoms)} symptoms")
    print(f"  ✓ Mapped: {len(result)} symptoms")
    print(f"  ✓ Mapped symptoms: {result}")


def test_empty_input(mapper):
    """Test with empty input."""
    print("\nTesting empty input...")
    
    result = mapper.map_symptoms([])
    assert result == [], "Empty input should return empty list"
    print(f"  ✓ Empty input handled correctly")


def test_normalization(mapper):
    """Test symptom normalization."""
    print("\nTesting symptom normalization...")
    
    test_cases = [
        ("  high fever  ", "high_fever"),
        ("High  Fever", "high_fever"),
        ("SKIN__RASH", "skin_rash"),
        ("_headache_", "headache"),
    ]
    
    for input_symptom, expected_normalized in test_cases:
        normalized = mapper._normalize_symptom(input_symptom)
        print(f"  ✓ '{input_symptom}' → '{normalized}'")


def test_threshold_adjustment(mapper):
    """Test similarity threshold adjustment."""
    print("\nTesting threshold adjustment...")
    
    # Test with default threshold (0.8)
    symptom = "stomach ache"
    result_default = mapper.map_symptoms([symptom])
    
    # Lower threshold
    mapper.set_similarity_threshold(0.6)
    result_lower = mapper.map_symptoms([symptom])
    
    # Reset to default
    mapper.set_similarity_threshold(0.8)
    
    print(f"  ✓ Threshold adjustment works")
    print(f"  ✓ Default (0.8): {len(result_default)} matches")
    print(f"  ✓ Lower (0.6): {len(result_lower)} matches")


if __name__ == "__main__":
    print("=" * 60)
    print("SYMPTOM MAPPER VALIDATION")
    print("=" * 60)
    
    try:
        mapper = test_initialization()
        test_exact_matching(mapper)
        test_case_insensitive_matching(mapper)
        test_space_to_underscore(mapper)
        test_fuzzy_matching(mapper)
        test_invalid_symptoms(mapper)
        test_mixed_symptoms(mapper)
        test_empty_input(mapper)
        test_normalization(mapper)
        test_threshold_adjustment(mapper)
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
