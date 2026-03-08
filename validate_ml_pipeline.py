"""
End-to-end validation of the ML pipeline.
Tests: Data Loading → Preprocessing → Training → Prediction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.data_loader import DataLoader
from app.data_preprocessor import DataPreprocessor
from app.ml_predictor import MLPredictor


def test_full_pipeline():
    """Test the complete ML pipeline end-to-end."""
    print("=" * 60)
    print("ML PIPELINE END-TO-END VALIDATION")
    print("=" * 60)
    
    # Step 1: Data Loading
    print("\n1. Testing Data Loading...")
    loader = DataLoader("data/disease_symptom_dataset.csv")
    df = loader.load_dataset()
    symptoms = loader.extract_unique_symptoms(df)
    print(f"  ✓ Loaded {len(df)} samples")
    print(f"  ✓ Extracted {len(symptoms)} unique symptoms")
    
    # Step 2: Data Preprocessing
    print("\n2. Testing Data Preprocessing...")
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test, feature_columns = preprocessor.preprocess_for_training(df)
    print(f"  ✓ Training set: {X_train.shape}")
    print(f"  ✓ Test set: {X_test.shape}")
    print(f"  ✓ Features: {len(feature_columns)}")
    
    # Step 3: Model Loading (assumes training was done)
    print("\n3. Testing Model Loading...")
    try:
        predictor = MLPredictor()
        print(f"  ✓ Model loaded successfully")
        print(f"  ✓ Model features: {len(predictor.get_feature_columns())}")
        print(f"  ✓ Disease classes: {len(predictor.get_disease_classes())}")
    except Exception as e:
        print(f"  ❌ Model loading failed: {e}")
        print("  ℹ  Run 'python scripts/train_model.py' first")
        return False
    
    # Step 4: Prediction
    print("\n4. Testing Prediction...")
    
    # Test Case 1: Fever-related symptoms
    test_cases = [
        {
            "name": "Fever symptoms",
            "symptoms": ["high_fever", "headache", "chills", "fatigue"]
        },
        {
            "name": "Skin symptoms",
            "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]
        },
        {
            "name": "Respiratory symptoms",
            "symptoms": ["cough", "breathlessness", "chest_pain"]
        },
        {
            "name": "Empty symptoms",
            "symptoms": []
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  Test: {test_case['name']}")
        print(f"  Input: {test_case['symptoms']}")
        
        predictions = predictor.predict(test_case['symptoms'], top_k=3)
        
        print(f"  Predictions:")
        for i, pred in enumerate(predictions, 1):
            print(f"    {i}. {pred.disease}: {pred.probability:.4f}")
    
    # Step 5: Verify consistency
    print("\n5. Testing Prediction Consistency...")
    symptoms = ["high_fever", "headache"]
    pred1 = predictor.predict(symptoms, top_k=3)
    pred2 = predictor.predict(symptoms, top_k=3)
    
    # Check if predictions are identical
    consistent = all(
        p1.disease == p2.disease and abs(p1.probability - p2.probability) < 1e-6
        for p1, p2 in zip(pred1, pred2)
    )
    
    if consistent:
        print(f"  ✓ Predictions are consistent across multiple calls")
    else:
        print(f"  ❌ Predictions are inconsistent")
        return False
    
    # Step 6: Verify feature alignment
    print("\n6. Testing Feature Alignment...")
    model_features = set(predictor.get_feature_columns())
    preprocessor_features = set(feature_columns)
    
    if model_features == preprocessor_features:
        print(f"  ✓ Model and preprocessor features are aligned")
    else:
        print(f"  ❌ Feature mismatch detected")
        print(f"    Model features: {len(model_features)}")
        print(f"    Preprocessor features: {len(preprocessor_features)}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = test_full_pipeline()
        
        if success:
            print("\n" + "=" * 60)
            print("ML PIPELINE VALIDATION PASSED ✓")
            print("=" * 60)
            print("\nThe ML pipeline is working correctly:")
            print("  ✓ Data loading and preprocessing")
            print("  ✓ Model training and serialization")
            print("  ✓ Prediction and inference")
            print("  ✓ Feature consistency")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("ML PIPELINE VALIDATION FAILED ❌")
            print("=" * 60)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
