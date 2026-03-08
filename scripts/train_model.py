"""
ML model training script for SwasthyaAI Lite.
Trains multiple models and selects the best one based on weighted F1 score.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    f1_score,
    accuracy_score
)
import joblib
import json
import numpy as np
from datetime import datetime
import logging

from app.data_loader import DataLoader
from app.data_preprocessor import DataPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLTrainer:
    """Handles training and evaluation of ML models for disease prediction."""
    
    def __init__(self, dataset_path: str = "data/disease_symptom_dataset.csv"):
        """
        Initialize MLTrainer.
        
        Args:
            dataset_path: Path to the disease symptom dataset
        """
        self.dataset_path = dataset_path
        self.models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=100, 
                random_state=42,
                n_jobs=-1
            ),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=100, 
                random_state=42
            ),
            "LogisticRegression": LogisticRegression(
                max_iter=1000, 
                random_state=42,
                n_jobs=-1
            )
        }
        self.best_model = None
        self.best_model_name = None
        self.training_metrics = {}
    
    def train_and_evaluate(self) -> str:
        """
        Train all models, evaluate, and save the best one.
        
        Returns:
            Name of the best model
        """
        logger.info("=" * 60)
        logger.info("STARTING MODEL TRAINING")
        logger.info("=" * 60)
        
        # Load and preprocess data
        logger.info("\n1. Loading and preprocessing data...")
        loader = DataLoader(self.dataset_path)
        df = loader.load_dataset()
        
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, feature_columns = preprocessor.preprocess_for_training(df)
        
        logger.info(f"Training samples: {X_train.shape[0]}")
        logger.info(f"Test samples: {X_test.shape[0]}")
        logger.info(f"Features: {X_train.shape[1]}")
        logger.info(f"Classes: {len(preprocessor.get_label_encoder().classes_)}")
        
        # Train and evaluate each model
        logger.info("\n2. Training and evaluating models...")
        best_f1 = 0.0
        
        for model_name, model in self.models.items():
            logger.info(f"\n--- Training {model_name} ---")
            
            # Train model
            model.fit(X_train, y_train)
            logger.info(f"✓ {model_name} training complete")
            
            # Perform 5-fold cross-validation on training set
            cv_scores = cross_val_score(
                model, X_train, y_train, 
                cv=5, 
                scoring='f1_weighted',
                n_jobs=-1
            )
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            logger.info(f"Cross-validation F1 (weighted): {cv_mean:.4f} (+/- {cv_std:.4f})")
            
            # Evaluate on test set
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1_weighted = f1_score(y_test, y_pred, average='weighted')
            
            logger.info(f"Test Accuracy: {accuracy:.4f}")
            logger.info(f"Test F1 (weighted): {f1_weighted:.4f}")
            
            # Store metrics
            self.training_metrics[model_name] = {
                "accuracy": float(accuracy),
                "f1_weighted": float(f1_weighted),
                "cv_f1_mean": float(cv_mean),
                "cv_f1_std": float(cv_std)
            }
            
            # Track best model
            if f1_weighted > best_f1:
                best_f1 = f1_weighted
                self.best_model = model
                self.best_model_name = model_name
        
        # Print detailed evaluation for best model
        logger.info("\n" + "=" * 60)
        logger.info(f"BEST MODEL: {self.best_model_name}")
        logger.info(f"Best F1 Score (weighted): {best_f1:.4f}")
        logger.info("=" * 60)
        
        # Generate detailed report for best model
        y_pred_best = self.best_model.predict(X_test)
        
        logger.info("\n3. Classification Report (Best Model):")
        logger.info("\n" + classification_report(
            y_test, y_pred_best,
            target_names=preprocessor.get_label_encoder().classes_
        ))
        
        logger.info("\n4. Confusion Matrix (Best Model):")
        cm = confusion_matrix(y_test, y_pred_best)
        logger.info(f"Shape: {cm.shape}")
        logger.info(f"Diagonal sum (correct predictions): {np.trace(cm)}")
        logger.info(f"Total predictions: {np.sum(cm)}")
        
        # Save models and artifacts
        logger.info("\n5. Saving model artifacts...")
        self._save_artifacts(
            self.best_model,
            feature_columns,
            preprocessor.get_label_encoder(),
            cm
        )
        
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING COMPLETE ✓")
        logger.info("=" * 60)
        
        return self.best_model_name
    
    def _save_artifacts(self, model, feature_columns, label_encoder, confusion_matrix):
        """
        Save model artifacts to disk.
        
        Args:
            model: Trained model
            feature_columns: List of feature names
            label_encoder: Fitted label encoder
            confusion_matrix: Confusion matrix array
        """
        # Create models directory if it doesn't exist
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # Save best model
        model_path = models_dir / "best_model.joblib"
        joblib.dump(model, model_path)
        logger.info(f"✓ Saved model to {model_path}")
        
        # Save feature columns
        features_path = models_dir / "feature_columns.joblib"
        joblib.dump(feature_columns, features_path)
        logger.info(f"✓ Saved feature columns to {features_path}")
        
        # Save label encoder
        encoder_path = models_dir / "label_encoder.joblib"
        joblib.dump(label_encoder, encoder_path)
        logger.info(f"✓ Saved label encoder to {encoder_path}")
        
        # Save confusion matrix
        cm_path = models_dir / "confusion_matrix.npy"
        np.save(cm_path, confusion_matrix)
        logger.info(f"✓ Saved confusion matrix to {cm_path}")
        
        # Save training metrics
        metrics_path = models_dir / "training_metrics.json"
        metrics_data = {
            "best_model": self.best_model_name,
            "timestamp": datetime.now().isoformat(),
            "models": self.training_metrics
        }
        with open(metrics_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        logger.info(f"✓ Saved training metrics to {metrics_path}")


def main():
    """Main training function with command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Train ML models for SwasthyaAI Lite disease prediction"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/disease_symptom_dataset.csv",
        help="Path to the disease symptom dataset CSV file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info(f"Using dataset: {args.dataset}")
        trainer = MLTrainer(dataset_path=args.dataset)
        best_model_name = trainer.train_and_evaluate()
        print(f"\n✓ Training successful! Best model: {best_model_name}")
        print(f"✓ Model artifacts saved to: models/")
        return 0
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
