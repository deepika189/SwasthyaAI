"""
Risk scoring engine for SwasthyaAI Lite.
Calculates risk scores and generates referral recommendations.
"""

from typing import List, Tuple
import logging

from app.ml_predictor import PredictionResult

logger = logging.getLogger(__name__)


class RiskScoringEngine:
    """Calculates risk scores and generates referral recommendations."""
    
    def __init__(self):
        """Initialize the risk scoring engine with thresholds."""
        self.high_risk_threshold = 0.70
        self.medium_risk_threshold = 0.40
        
        logger.info("RiskScoringEngine initialized")
    
    def calculate_risk(
        self,
        top_predictions: List[PredictionResult],
        num_symptoms: int
    ) -> Tuple[str, str, str]:
        """
        Calculate risk level, confidence, and referral recommendation.
        
        Args:
            top_predictions: List of prediction results (sorted by probability)
            num_symptoms: Number of symptoms provided by user
            
        Returns:
            Tuple of (risk_level, confidence_level, referral_recommendation)
        """
        # Get highest prediction probability
        if not top_predictions:
            max_probability = 0.0
        else:
            max_probability = top_predictions[0].probability
        
        # Determine risk level
        risk_level = self._determine_risk_level(max_probability)
        
        # Determine confidence level
        confidence_level = self._determine_confidence(num_symptoms)
        
        # Generate referral recommendation
        referral_recommendation = self._generate_referral(risk_level)
        
        logger.info(
            f"Risk assessment: Risk={risk_level}, "
            f"Confidence={confidence_level}, "
            f"Probability={max_probability:.4f}, "
            f"Symptoms={num_symptoms}"
        )
        
        return risk_level, confidence_level, referral_recommendation
    
    def _determine_risk_level(self, max_probability: float) -> str:
        """
        Determine risk level from highest prediction probability.
        
        Args:
            max_probability: Highest prediction probability (0-1)
            
        Returns:
            Risk level: "High", "Medium", or "Low"
        """
        if max_probability >= self.high_risk_threshold:
            return "High"
        elif max_probability >= self.medium_risk_threshold:
            return "Medium"
        else:
            return "Low"
    
    def _determine_confidence(self, num_symptoms: int) -> str:
        """
        Determine confidence level based on number of symptoms.
        
        Args:
            num_symptoms: Number of symptoms provided
            
        Returns:
            Confidence level: "Low", "Medium", or "High"
        """
        if num_symptoms < 2:
            return "Low"
        elif num_symptoms < 4:
            return "Medium"
        else:
            return "High"
    
    def _generate_referral(self, risk_level: str) -> str:
        """
        Generate referral recommendation based on risk level.
        
        Args:
            risk_level: Risk level ("High", "Medium", or "Low")
            
        Returns:
            Referral recommendation string
        """
        referrals = {
            "High": "Immediate PHC referral required",
            "Medium": "Visit PHC within 24 hours",
            "Low": "Home care monitoring recommended"
        }
        
        return referrals.get(risk_level, "Consult healthcare professional")
    
    def set_thresholds(self, high_threshold: float, medium_threshold: float):
        """
        Set custom risk thresholds.
        
        Args:
            high_threshold: Threshold for high risk (0-1)
            medium_threshold: Threshold for medium risk (0-1)
            
        Raises:
            ValueError: If thresholds are invalid
        """
        if not 0.0 <= high_threshold <= 1.0:
            raise ValueError("High threshold must be between 0.0 and 1.0")
        if not 0.0 <= medium_threshold <= 1.0:
            raise ValueError("Medium threshold must be between 0.0 and 1.0")
        if medium_threshold >= high_threshold:
            raise ValueError("Medium threshold must be less than high threshold")
        
        self.high_risk_threshold = high_threshold
        self.medium_risk_threshold = medium_threshold
        
        logger.info(f"Thresholds updated: High={high_threshold}, Medium={medium_threshold}")


# Convenience function for quick risk assessment
def assess_risk(predictions: List[PredictionResult], num_symptoms: int) -> Tuple[str, str, str]:
    """
    Assess risk using default engine.
    
    Args:
        predictions: List of prediction results
        num_symptoms: Number of symptoms provided
        
    Returns:
        Tuple of (risk_level, confidence_level, referral_recommendation)
    """
    engine = RiskScoringEngine()
    return engine.calculate_risk(predictions, num_symptoms)
