"""
Data preprocessing module for ML model training.
Handles feature extraction, encoding, and train-test splitting.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handles preprocessing of disease symptom data for ML training."""
    
    def __init__(self):
        """Initialize the preprocessor."""
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
    
    def preprocess_for_training(
        self, 
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Preprocess dataset for ML training.
        
        Args:
            df: DataFrame with Disease and Symptom columns
            test_size: Proportion of data for testing (default 0.2)
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test, feature_columns)
        """
        logger.info("Starting data preprocessing...")
        
        # Extract features and labels
        X, y, feature_columns = self._create_feature_matrix(df)
        self.feature_columns = feature_columns
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        logger.info(f"Encoded {len(self.label_encoder.classes_)} disease classes")
        
        # Stratified train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, 
            y_encoded,
            test_size=test_size,
            random_state=random_state,
            stratify=y_encoded  # Maintain class distribution
        )
        
        logger.info(f"Train set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        return X_train, X_test, y_train, y_test, feature_columns
    
    def _create_feature_matrix(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Create binary feature matrix from symptom columns.
        
        Args:
            df: DataFrame with Disease and Symptom columns
            
        Returns:
            Tuple of (feature_matrix, labels, feature_column_names)
        """
        # Extract disease labels
        y = df['Disease'].values
        
        # Get symptom columns
        symptom_columns = [col for col in df.columns if col.startswith('Symptom_')]
        
        # Collect all unique symptoms
        all_symptoms = set()
        for col in symptom_columns:
            symptoms = df[col].dropna().str.strip()
            symptoms = symptoms[symptoms != '']
            all_symptoms.update(symptoms)
        
        # Sort for consistent ordering
        feature_columns = sorted(list(all_symptoms))
        logger.info(f"Created {len(feature_columns)} binary features")
        
        # Create binary feature matrix
        n_samples = len(df)
        n_features = len(feature_columns)
        X = np.zeros((n_samples, n_features), dtype=np.int8)
        
        # Fill feature matrix
        for idx, row in df.iterrows():
            # Get all symptoms for this row
            row_symptoms = []
            for col in symptom_columns:
                symptom = row[col]
                if pd.notna(symptom) and str(symptom).strip() != '':
                    row_symptoms.append(str(symptom).strip())
            
            # Set binary features
            for symptom in row_symptoms:
                if symptom in feature_columns:
                    feature_idx = feature_columns.index(symptom)
                    X[idx, feature_idx] = 1
        
        return X, y, feature_columns
    
    def get_label_encoder(self) -> LabelEncoder:
        """Get the fitted label encoder."""
        return self.label_encoder
    
    def get_feature_columns(self) -> List[str]:
        """Get the list of feature column names."""
        return self.feature_columns


def verify_stratification(y_train: np.ndarray, y_test: np.ndarray, tolerance: float = 0.05) -> bool:
    """
    Verify that train and test sets have similar class distributions.
    
    Args:
        y_train: Training labels
        y_test: Test labels
        tolerance: Maximum allowed difference in proportions (default 5%)
        
    Returns:
        True if distributions are similar within tolerance
    """
    # Get unique classes
    classes = np.unique(np.concatenate([y_train, y_test]))
    
    # Calculate proportions
    train_total = len(y_train)
    test_total = len(y_test)
    
    max_diff = 0.0
    for cls in classes:
        train_prop = np.sum(y_train == cls) / train_total
        test_prop = np.sum(y_test == cls) / test_total
        diff = abs(train_prop - test_prop)
        max_diff = max(max_diff, diff)
    
    logger.info(f"Maximum class distribution difference: {max_diff:.4f}")
    return max_diff <= tolerance
