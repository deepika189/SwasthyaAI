"""
Unit tests for data loading module.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_loader import DataLoader, DatasetValidationError


def test_load_dataset_success():
    """Test successful dataset loading."""
    loader = DataLoader("data/disease_symptom_dataset.csv")
    df = loader.load_dataset()
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Disease' in df.columns
    assert len([col for col in df.columns if col.startswith('Symptom_')]) > 0


def test_load_dataset_file_not_found():
    """Test error handling when dataset file is missing."""
    loader = DataLoader("nonexistent_file.csv")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_dataset()
    
    assert "data/disease_symptom_dataset.csv" in str(exc_info.value)


def test_extract_unique_symptoms():
    """Test extraction of unique symptoms."""
    loader = DataLoader("data/disease_symptom_dataset.csv")
    df = loader.load_dataset()
    symptoms = loader.extract_unique_symptoms(df)
    
    assert isinstance(symptoms, set)
    assert len(symptoms) > 0
    # Check that symptoms are strings
    assert all(isinstance(s, str) for s in symptoms)
    # Check that symptoms are not empty
    assert all(len(s.strip()) > 0 for s in symptoms)


def test_load_and_extract():
    """Test combined load and extract operation."""
    loader = DataLoader("data/disease_symptom_dataset.csv")
    df, symptoms = loader.load_and_extract()
    
    assert isinstance(df, pd.DataFrame)
    assert isinstance(symptoms, set)
    assert not df.empty
    assert len(symptoms) > 0


if __name__ == "__main__":
    # Run basic validation
    print("Testing data loader...")
    test_load_dataset_success()
    print("✓ Dataset loads successfully")
    
    test_extract_unique_symptoms()
    print("✓ Unique symptoms extracted")
    
    test_load_and_extract()
    print("✓ Combined load and extract works")
    
    print("\nAll tests passed!")
