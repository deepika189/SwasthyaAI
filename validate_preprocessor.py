"""
Validation script for data preprocessor.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.data_loader import DataLoader
from app.data_preprocessor import DataPreprocessor, verify_stratification
import numpy as np


def test_preprocessing():
    """Test data preprocessing."""
    print("Testing data preprocessing...")
    
    # Load data
    loader = DataLoader("data/disease_symptom_dataset.csv")
    df = loader.load_dataset()
    print(f"  ✓ Loaded {len(df)} samples")
    
    # Preprocess
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test, feature_columns = preprocessor.preprocess_for_training(df)
    
    # Validate shapes
    assert X_train.shape[0] > 0, "Training set is empty"
    assert X_test.shape[0] > 0, "Test set is empty"
    assert X_train.shape[1] == len(feature_columns), "Feature count mismatch"
    
    print(f"  ✓ Training set: {X_train.shape}")
    print(f"  ✓ Test set: {X_test.shape}")
    print(f"  ✓ Features: {len(feature_columns)}")
    
    return X_train, X_test, y_train, y_test, feature_columns, preprocessor


def test_binary_encoding(X_train):
    """Test that features are binary."""
    print("\nTesting binary encoding...")
    
    unique_values = np.unique(X_train)
    assert set(unique_values).issubset({0, 1}), "Features must be binary (0 or 1)"
    
    print(f"  ✓ All features are binary")
    print(f"  ✓ Unique values: {unique_values}")


def test_stratification(y_train, y_test):
    """Test stratified split."""
    print("\nTesting stratified split...")
    
    is_stratified = verify_stratification(y_train, y_test, tolerance=0.05)
    assert is_stratified, "Class distribution differs by more than 5%"
    
    print(f"  ✓ Stratification verified (within 5% tolerance)")
    
    # Show some class distributions
    unique_classes = np.unique(y_train)
    print(f"  ✓ Number of classes: {len(unique_classes)}")
    
    # Sample a few classes
    for cls in unique_classes[:3]:
        train_count = np.sum(y_train == cls)
        test_count = np.sum(y_test == cls)
        train_prop = train_count / len(y_train)
        test_prop = test_count / len(y_test)
        print(f"    Class {cls}: Train={train_prop:.3f}, Test={test_prop:.3f}")


def test_label_encoding(preprocessor):
    """Test label encoding."""
    print("\nTesting label encoding...")
    
    encoder = preprocessor.get_label_encoder()
    classes = encoder.classes_
    
    assert len(classes) > 0, "No classes encoded"
    print(f"  ✓ Encoded {len(classes)} disease classes")
    print(f"  ✓ Sample classes: {classes[:5]}")


def test_feature_columns(feature_columns):
    """Test feature columns."""
    print("\nTesting feature columns...")
    
    assert len(feature_columns) > 0, "No feature columns"
    assert all(isinstance(f, str) for f in feature_columns), "Features must be strings"
    
    print(f"  ✓ {len(feature_columns)} feature columns")
    print(f"  ✓ Sample features: {feature_columns[:5]}")


if __name__ == "__main__":
    print("=" * 60)
    print("DATA PREPROCESSOR VALIDATION")
    print("=" * 60)
    
    try:
        X_train, X_test, y_train, y_test, feature_columns, preprocessor = test_preprocessing()
        test_binary_encoding(X_train)
        test_stratification(y_train, y_test)
        test_label_encoding(preprocessor)
        test_feature_columns(feature_columns)
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
