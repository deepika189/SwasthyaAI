"""
Simple validation script for data loader (no dependencies required).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.data_loader import DataLoader, DatasetValidationError


def test_load_dataset():
    """Test dataset loading."""
    print("Testing dataset loading...")
    loader = DataLoader("data/disease_symptom_dataset.csv")
    df = loader.load_dataset()
    
    assert 'Disease' in df.columns, "Disease column not found"
    symptom_cols = [col for col in df.columns if col.startswith('Symptom_')]
    assert len(symptom_cols) > 0, "No symptom columns found"
    
    print(f"  ✓ Loaded {len(df)} rows")
    print(f"  ✓ Found {len(symptom_cols)} symptom columns")
    print(f"  ✓ Found {df['Disease'].nunique()} unique diseases")
    return df


def test_extract_symptoms(df):
    """Test symptom extraction."""
    print("\nTesting symptom extraction...")
    loader = DataLoader("data/disease_symptom_dataset.csv")
    symptoms = loader.extract_unique_symptoms(df)
    
    assert len(symptoms) > 0, "No symptoms extracted"
    assert all(isinstance(s, str) for s in symptoms), "Symptoms must be strings"
    
    print(f"  ✓ Extracted {len(symptoms)} unique symptoms")
    print(f"  ✓ Sample symptoms: {list(symptoms)[:5]}")
    return symptoms


def test_missing_file():
    """Test error handling for missing file."""
    print("\nTesting missing file error handling...")
    loader = DataLoader("nonexistent.csv")
    
    try:
        loader.load_dataset()
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        print(f"  ✓ Correctly raised FileNotFoundError")
        print(f"  ✓ Error message: {str(e)[:80]}...")


def test_schema_validation():
    """Test schema validation."""
    print("\nTesting schema validation...")
    loader = DataLoader("data/disease_symptom_dataset.csv")
    df = loader.load_dataset()
    
    # This should pass without errors
    print("  ✓ Schema validation passed")


if __name__ == "__main__":
    print("=" * 60)
    print("DATA LOADER VALIDATION")
    print("=" * 60)
    
    try:
        df = test_load_dataset()
        symptoms = test_extract_symptoms(df)
        test_missing_file()
        test_schema_validation()
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
