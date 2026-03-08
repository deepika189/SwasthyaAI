"""
Symptom mapping module for SwasthyaAI Lite.
Maps extracted symptoms to dataset feature columns using fuzzy matching.
"""

from typing import List, Set, Optional
from difflib import SequenceMatcher
from pathlib import Path
import logging

from app.data_loader import DataLoader

logger = logging.getLogger(__name__)


class SymptomMapper:
    """Maps extracted symptoms to valid dataset feature columns."""
    
    def __init__(self, dataset_path: str = "data/disease_symptom_dataset.csv"):
        """
        Initialize SymptomMapper.
        
        Args:
            dataset_path: Path to the disease symptom dataset
        """
        self.dataset_path = dataset_path
        self.similarity_threshold = 0.8
        self.valid_symptoms = self._load_valid_symptoms()
        
        logger.info(f"SymptomMapper initialized with {len(self.valid_symptoms)} valid symptoms")
    
    def _load_valid_symptoms(self) -> Set[str]:
        """
        Load all unique symptoms from dataset columns.
        
        Returns:
            Set of valid symptom strings
        """
        loader = DataLoader(self.dataset_path)
        df = loader.load_dataset()
        symptoms = loader.extract_unique_symptoms(df)
        
        # Normalize all symptoms
        normalized_symptoms = {self._normalize_symptom(s) for s in symptoms}
        
        return normalized_symptoms
    
    def map_symptoms(self, extracted_symptoms: List[str]) -> List[str]:
        """
        Map extracted symptoms to valid dataset features.
        
        Args:
            extracted_symptoms: List of symptom strings from LLM extraction
            
        Returns:
            List of valid feature names that match the dataset
        """
        mapped_symptoms = []
        
        for symptom in extracted_symptoms:
            # Normalize the symptom
            normalized = self._normalize_symptom(symptom)
            
            # Try exact match first
            if normalized in self.valid_symptoms:
                mapped_symptoms.append(normalized)
                logger.debug(f"Exact match: '{symptom}' → '{normalized}'")
            else:
                # Try fuzzy matching
                matched = self._fuzzy_match(normalized)
                if matched:
                    mapped_symptoms.append(matched)
                    logger.debug(f"Fuzzy match: '{symptom}' → '{matched}'")
                else:
                    logger.debug(f"No match found for: '{symptom}'")
        
        logger.info(f"Mapped {len(mapped_symptoms)}/{len(extracted_symptoms)} symptoms")
        return mapped_symptoms
    
    def _normalize_symptom(self, symptom: str) -> str:
        """
        Normalize symptom text.
        
        Args:
            symptom: Raw symptom string
            
        Returns:
            Normalized symptom string (lowercase, stripped, underscores)
        """
        # Convert to lowercase, strip whitespace, replace spaces with underscores
        normalized = symptom.lower().strip().replace(" ", "_")
        
        # Remove multiple consecutive underscores
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        
        # Remove leading/trailing underscores
        normalized = normalized.strip("_")
        
        return normalized
    
    def _fuzzy_match(self, symptom: str) -> Optional[str]:
        """
        Find best matching valid symptom using fuzzy matching.
        
        Args:
            symptom: Normalized symptom string
            
        Returns:
            Best matching valid symptom, or None if no match above threshold
        """
        best_match = None
        best_score = 0.0
        
        for valid_symptom in self.valid_symptoms:
            # Calculate similarity score
            score = SequenceMatcher(None, symptom, valid_symptom).ratio()
            
            if score > best_score:
                best_score = score
                best_match = valid_symptom
        
        # Return match only if above threshold
        if best_score >= self.similarity_threshold:
            logger.debug(f"Fuzzy match score: {best_score:.3f} for '{symptom}' → '{best_match}'")
            return best_match
        
        return None
    
    def get_valid_symptoms(self) -> List[str]:
        """Get list of all valid symptoms."""
        return sorted(list(self.valid_symptoms))
    
    def set_similarity_threshold(self, threshold: float):
        """
        Set the similarity threshold for fuzzy matching.
        
        Args:
            threshold: Similarity threshold (0.0 to 1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        
        self.similarity_threshold = threshold
        logger.info(f"Similarity threshold set to {threshold}")


# Convenience function for quick mapping
def map_symptoms_to_features(symptoms: List[str]) -> List[str]:
    """
    Map symptoms to valid features using default mapper.
    
    Args:
        symptoms: List of symptom strings
        
    Returns:
        List of valid feature names
    """
    mapper = SymptomMapper()
    return mapper.map_symptoms(symptoms)
