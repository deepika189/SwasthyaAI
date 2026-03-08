"""
Validation script for Bedrock integration (using mock for testing).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.bedrock_integration import MockBedrockSymptomExtractor, BedrockSymptomExtractor


def test_mock_extractor():
    """Test mock extractor functionality."""
    print("Testing Mock Bedrock Extractor...")
    
    extractor = MockBedrockSymptomExtractor()
    
    test_cases = [
        {
            "input": "Patient has fever and headache",
            "description": "English symptoms"
        },
        {
            "input": "Mujhe bukhar aur sir dard hai",
            "description": "Hindi symptoms"
        },
        {
            "input": "I have cough, fatigue, and chills",
            "description": "Multiple symptoms"
        },
        {
            "input": "Patient complaining of itching and rash",
            "description": "Skin symptoms"
        },
        {
            "input": "",
            "description": "Empty input"
        },
    ]
    
    for test_case in test_cases:
        symptoms = extractor.extract_symptoms(test_case["input"])
        print(f"\n  Test: {test_case['description']}")
        print(f"  Input: '{test_case['input']}'")
        print(f"  Extracted: {symptoms}")
        print(f"  ✓ Extracted {len(symptoms)} symptoms")
    
    return extractor


def test_empty_input(extractor):
    """Test with empty input."""
    print("\nTesting empty input handling...")
    
    empty_inputs = ["", "   ", None]
    
    for empty_input in empty_inputs:
        if empty_input is None:
            continue
        symptoms = extractor.extract_symptoms(empty_input)
        assert symptoms == [], f"Empty input should return empty list, got {symptoms}"
    
    print(f"  ✓ Empty inputs handled correctly")


def test_diagnosis_filtering():
    """Test that diagnosis keywords are filtered."""
    print("\nTesting diagnosis keyword filtering...")
    
    extractor = BedrockSymptomExtractor()
    
    test_texts = [
        "diagnosis of malaria",
        "treatment for fever",
        "prescription needed",
        "medication for pain",
        "the disease is serious",
    ]
    
    for text in test_texts:
        contains_diagnosis = extractor._contains_diagnosis_keywords(text)
        assert contains_diagnosis, f"Should detect diagnosis keyword in: {text}"
        print(f"  ✓ Detected diagnosis keyword in: '{text}'")


def test_prompt_building():
    """Test prompt building."""
    print("\nTesting prompt building...")
    
    extractor = BedrockSymptomExtractor()
    
    test_input = "Patient has fever and headache"
    prompt = extractor._build_prompt(test_input)
    
    assert "fever and headache" in prompt, "Input should be in prompt"
    assert "ONLY" in prompt, "Guardrails should be present"
    assert "diagnosis" in prompt.lower(), "Should mention not to diagnose"
    assert "JSON" in prompt, "Should specify JSON format"
    
    print(f"  ✓ Prompt built correctly")
    print(f"  ✓ Prompt length: {len(prompt)} characters")


def test_json_parsing():
    """Test JSON response parsing."""
    print("\nTesting JSON response parsing...")
    
    extractor = BedrockSymptomExtractor()
    
    # Mock Claude response
    mock_claude_response = {
        "content": [
            {
                "text": '["fever", "headache", "cough"]'
            }
        ]
    }
    
    symptoms = extractor._parse_response(mock_claude_response)
    assert len(symptoms) == 3, f"Expected 3 symptoms, got {len(symptoms)}"
    assert "fever" in symptoms, "Should extract 'fever'"
    
    print(f"  ✓ Parsed Claude response: {symptoms}")
    
    # Test with extra text around JSON
    mock_response_with_text = {
        "content": [
            {
                "text": 'Here are the symptoms: ["fever", "headache"] from the input.'
            }
        ]
    }
    
    symptoms = extractor._parse_response(mock_response_with_text)
    assert len(symptoms) == 2, f"Expected 2 symptoms, got {len(symptoms)}"
    
    print(f"  ✓ Parsed response with extra text: {symptoms}")


def test_initialization():
    """Test extractor initialization."""
    print("\nTesting extractor initialization...")
    
    # Test with default parameters
    extractor1 = BedrockSymptomExtractor()
    assert extractor1.temperature == 0.0, "Temperature should be 0.0"
    assert extractor1.max_retries == 2, "Max retries should be 2"
    
    print(f"  ✓ Default initialization")
    print(f"  ✓ Model: {extractor1.model_id}")
    print(f"  ✓ Region: {extractor1.region}")
    print(f"  ✓ Temperature: {extractor1.temperature}")
    
    # Test with custom parameters
    extractor2 = BedrockSymptomExtractor(
        model_id="custom-model",
        region="us-west-2"
    )
    assert extractor2.model_id == "custom-model"
    assert extractor2.region == "us-west-2"
    
    print(f"  ✓ Custom initialization works")


if __name__ == "__main__":
    print("=" * 60)
    print("BEDROCK INTEGRATION VALIDATION")
    print("=" * 60)
    print("\nNote: Using mock extractor (no AWS credentials required)")
    
    try:
        extractor = test_mock_extractor()
        test_empty_input(extractor)
        test_diagnosis_filtering()
        test_prompt_building()
        test_json_parsing()
        test_initialization()
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        print("\nNote: Real Bedrock integration requires:")
        print("  - AWS credentials configured")
        print("  - Bedrock service access enabled")
        print("  - Appropriate IAM permissions")
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
