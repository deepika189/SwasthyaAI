"""
Data loading and validation module for SwasthyaAI Lite.
Handles loading the disease symptom dataset and extracting unique symptoms.
"""

import pandas as pd
from pathlib import Path
from typing import Set, Tuple
import logging

logger = logging.getLogger(__name__)


class DatasetValidationError(Exception):
    """Raised when dataset validation fails."""
    pass


class DataLoader:
    """Handles loading and validation of the disease symptom dataset."""
    
    def __init__(self, dataset_path: str = "data/disease_symptom_dataset.csv"):
        """
        Initialize DataLoader with dataset path.
        
        Args:
            dataset_path: Path to the disease symptom CSV file
        """
        self.dataset_path = Path(dataset_path)
        
    def load_dataset(self) -> pd.DataFrame:
        """
        Load the disease symptom dataset from CSV.
        
        Returns:
            DataFrame containing the disease symptom data
            
        Raises:
            FileNotFoundError: If dataset file is not found
            DatasetValidationError: If dataset schema is invalid
        """
        # Check if file exists
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset file not found at: {self.dataset_path.absolute()}\n"
                f"Expected path: data/disease_symptom_dataset.csv"
            )
        
        try:
            # Load CSV
            df = pd.read_csv(self.dataset_path)
            logger.info(f"Loaded dataset with {len(df)} rows")
            
            # Validate schema
            self._validate_schema(df)
            
            return df
            
        except pd.errors.EmptyDataError:
            raise DatasetValidationError("Dataset file is empty")
        except pd.errors.ParserError as e:
            raise DatasetValidationError(f"Failed to parse CSV file: {e}")
    
    def _validate_schema(self, df: pd.DataFrame) -> None:
        """
        Validate that the dataset has the expected schema.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            DatasetValidationError: If schema is invalid
        """
        # Check if DataFrame is empty
        if df.empty:
            raise DatasetValidationError("Dataset is empty")
        
        # Check for Disease column
        if 'Disease' not in df.columns:
            raise DatasetValidationError(
                "Dataset must have a 'Disease' column as the first column.\n"
                f"Found columns: {list(df.columns)}"
            )
        
        # Check for Symptom columns
        symptom_columns = [col for col in df.columns if col.startswith('Symptom_')]
        if len(symptom_columns) == 0:
            raise DatasetValidationError(
                "Dataset must have Symptom columns (Symptom_1, Symptom_2, etc.).\n"
                f"Found columns: {list(df.columns)}"
            )
        
        logger.info(f"Schema validation passed: {len(symptom_columns)} symptom columns found")
    
    def extract_unique_symptoms(self, df: pd.DataFrame) -> Set[str]:
        """
        Extract all unique symptoms from the dataset.
        
        Args:
            df: DataFrame containing disease symptom data
            
        Returns:
            Set of unique symptom strings
        """
        symptoms = set()
        
        # Get all symptom columns
        symptom_columns = [col for col in df.columns if col.startswith('Symptom_')]
        
        # Extract symptoms from each column
        for col in symptom_columns:
            # Get non-null values and strip whitespace
            col_symptoms = df[col].dropna().str.strip()
            # Filter out empty strings
            col_symptoms = col_symptoms[col_symptoms != '']
            # Add to set
            symptoms.update(col_symptoms)
        
        logger.info(f"Extracted {len(symptoms)} unique symptoms")
        return symptoms
    
    def load_and_extract(self) -> Tuple[pd.DataFrame, Set[str]]:
        """
        Load dataset and extract unique symptoms in one call.
        
        Returns:
            Tuple of (DataFrame, Set of unique symptoms)
        """
        df = self.load_dataset()
        symptoms = self.extract_unique_symptoms(df)
        return df, symptoms


# Convenience function for quick loading
def load_disease_symptom_dataset(dataset_path: str = "data/disease_symptom_dataset.csv") -> pd.DataFrame:
    """
    Load the disease symptom dataset.
    
    Args:
        dataset_path: Path to the CSV file
        
    Returns:
        DataFrame containing the dataset
    """
    loader = DataLoader(dataset_path)
    return loader.load_dataset()
