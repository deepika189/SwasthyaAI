"""
ML prediction module for disease prediction from symptoms.
"""

import joblib
import numpy as np
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class PredictionResult:
    """Represents a disease prediction with probability."""
    
    def __init__(self, disease: str, probability: float):
        """
        Initialize prediction result.
        
        Args:
            disease: Disease name
            probability: Prediction probability (0-1)
        """
        self.disease = disease
        self.probability = probability
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "disease": self.disease,
            "probability": float(self.probability)
        }
    
    def __repr__(self):
        return f"PredictionResult(disease='{self.disease}', probability={self.probability:.4f})"


class ModelLoadError(Exception):
    """Raised when model loading fails."""
    pass


class MLPredictor:
    """Handles disease prediction from structured symptoms using trained ML models."""
    
    def __init__(
        self,
        model_path: str = "models/best_model.joblib",
        feature_columns_path: str = "models/feature_columns.joblib",
        label_encoder_path: str = "models/label_encoder.joblib"
    ):
        """
        Initialize MLPredictor by loading trained model artifacts.
        
        Args:
            model_path: Path to trained model file
            feature_columns_path: Path to feature columns file
            label_encoder_path: Path to label encoder file
            
        Raises:
            ModelLoadError: If any model artifact fails to load
        """
        self.model_path = Path(model_path)
        self.feature_columns_path = Path(feature_columns_path)
        self.label_encoder_path = Path(label_encoder_path)
        
        # Load model artifacts
        self._load_artifacts()
        
        logger.info(f"MLPredictor initialized with {len(self.feature_columns)} features")
    
    def _load_artifacts(self):
        """Load all model artifacts from disk."""
        try:
            # Check if files exist
            if not self.model_path.exists():
                raise ModelLoadError(
                    f"Model file not found: {self.model_path.absolute()}\n"
                    "Please run training script first: python scripts/train_model.py"
                )
            
            if not self.feature_columns_path.exists():
                raise ModelLoadError(f"Feature columns file not found: {self.feature_columns_path.absolute()}")
            
            if not self.label_encoder_path.exists():
                raise ModelLoadError(f"Label encoder file not found: {self.label_encoder_path.absolute()}")
            
            # Load artifacts
            self.model = joblib.load(self.model_path)
            self.feature_columns = joblib.load(self.feature_columns_path)
            self.label_encoder = joblib.load(self.label_encoder_path)
            
            logger.info("Model artifacts loaded successfully")
            
        except Exception as e:
            if isinstance(e, ModelLoadError):
                raise
            raise ModelLoadError(f"Failed to load model artifacts: {e}")
    
    def predict(self, mapped_symptoms: List[str], top_k: int = 3) -> List[PredictionResult]:
        """
        Predict diseases from mapped symptoms.
        
        Args:
            mapped_symptoms: List of symptom strings (must match feature columns)
            top_k: Number of top predictions to return (default 3)
            
        Returns:
            List of PredictionResult objects, sorted by probability (highest first)
            
        Raises:
            ValueError: If top_k is invalid
        """
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        
        # Create feature vector
        feature_vector = self._create_feature_vector(mapped_symptoms)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(feature_vector)[0]
        
        # Get top K predictions
        top_k_indices = np.argsort(probabilities)[-top_k:][::-1]
        
        # Create prediction results
        results = []
        for idx in top_k_indices:
            disease = self.label_encoder.classes_[idx]
            probability = probabilities[idx]
            results.append(PredictionResult(disease, probability))
        
        logger.info(f"Generated {len(results)} predictions from {len(mapped_symptoms)} symptoms")
        
        return results
    
    def _create_feature_vector(self, mapped_symptoms: List[str]) -> np.ndarray:
        """
        Create binary feature vector from symptom list.
        
        Args:
            mapped_symptoms: List of symptom strings
            
        Returns:
            Binary feature vector (1D numpy array)
        """
        # Initialize feature vector with zeros
        feature_vector = np.zeros(len(self.feature_columns), dtype=np.int8)
        
        # Set features to 1 for present symptoms
        for symptom in mapped_symptoms:
            if symptom in self.feature_columns:
                idx = self.feature_columns.index(symptom)
                feature_vector[idx] = 1
        
        # Reshape to 2D array for sklearn (1 sample, n features)
        return feature_vector.reshape(1, -1)
    
    def get_feature_columns(self) -> List[str]:
        """Get list of feature column names."""
        return self.feature_columns.copy()
    
    def get_disease_classes(self) -> List[str]:
        """Get list of all disease classes."""
        return list(self.label_encoder.classes_)


# Convenience function for quick predictions
def predict_disease(symptoms: List[str], top_k: int = 3) -> List[PredictionResult]:
    """
    Predict diseases from symptoms using default model.
    
    Args:
        symptoms: List of symptom strings
        top_k: Number of top predictions to return
        
    Returns:
        List of PredictionResult objects
    """
    predictor = MLPredictor()
    return predictor.predict(symptoms, top_k)
