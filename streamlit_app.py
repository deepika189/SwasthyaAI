"""
SwasthyaAI Lite - Standalone Streamlit Application
Complete app with all backend logic integrated for easy deployment.
"""

import streamlit as st
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
import json

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all components
from app.bedrock_integration import BedrockSymptomExtractor, MockBedrockSymptomExtractor
from app.symptom_mapper import SymptomMapper
from app.ml_predictor import MLPredictor, PredictionResult
from app.risk_engine import RiskScoringEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="SwasthyaAI Lite",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .disclaimer {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1.5rem 0;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .risk-high {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .risk-medium {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .risk-low {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .prediction-card {
        background-color: #f8f9fa;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 3px solid #007bff;
    }
    .symptom-badge {
        display: inline-block;
        background-color: #e7f3ff;
        color: #0066cc;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 15px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_components():
    """Initialize all components (cached for performance)."""
    try:
        # Get configuration from environment or Streamlit secrets
        # Try Streamlit secrets first, then fall back to environment variables
        try:
            aws_region = st.secrets.get("AWS_REGION", "us-east-1")
            bedrock_model_id = st.secrets.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
            use_mock_bedrock = st.secrets.get("USE_MOCK_BEDROCK", "true").lower() == "true"
        except:
            # Fall back to environment variables
            aws_region = os.getenv("AWS_REGION", "us-east-1")
            bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
            use_mock_bedrock = os.getenv("USE_MOCK_BEDROCK", "true").lower() == "true"
        
        logger.info(f"Initializing components (Mock: {use_mock_bedrock})")
        
        # Initialize Bedrock extractor
        if use_mock_bedrock:
            bedrock_extractor = MockBedrockSymptomExtractor()
        else:
            bedrock_extractor = BedrockSymptomExtractor(
                model_id=bedrock_model_id,
                region=aws_region
            )
        
        # Initialize other components
        symptom_mapper = SymptomMapper(dataset_path="data/disease_symptom_dataset.csv")
        ml_predictor = MLPredictor(model_path="models/best_model.joblib")
        risk_engine = RiskScoringEngine()
        
        logger.info("All components initialized successfully")
        
        return bedrock_extractor, symptom_mapper, ml_predictor, risk_engine, None
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return None, None, None, None, str(e)


def analyze_symptoms_local(text_input: str, bedrock_extractor, symptom_mapper, ml_predictor, risk_engine):
    """Analyze symptoms using local components."""
    try:
        # Step 1: Extract symptoms
        extracted_symptoms = bedrock_extractor.extract_symptoms(text_input)
        logger.info(f"Extracted {len(extracted_symptoms)} symptoms")
        
        # Step 2: Map symptoms
        mapped_symptoms = symptom_mapper.map_symptoms(extracted_symptoms)
        logger.info(f"Mapped {len(mapped_symptoms)} symptoms")
        
        # Step 3: Predict diseases
        predictions = ml_predictor.predict(mapped_symptoms, top_k=3)
        logger.info(f"Generated {len(predictions)} predictions")
        
        # Step 4: Calculate risk
        risk_level, confidence_level, referral_recommendation = risk_engine.calculate_risk(
            predictions,
            num_symptoms=len(mapped_symptoms)
        )
        
        return {
            "extracted_symptoms": extracted_symptoms,
            "mapped_symptoms": mapped_symptoms,
            "top_predictions": [{"disease": p.disease, "probability": p.probability} for p in predictions],
            "risk_level": risk_level,
            "confidence_level": confidence_level,
            "referral_recommendation": referral_recommendation
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return None


def display_results(results: dict):
    """Display analysis results."""
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Extracted symptoms
    if results.get("extracted_symptoms"):
        st.markdown("### 🔍 Extracted Symptoms")
        symptoms_html = "".join([
            f'<span class="symptom-badge">{symptom}</span>' 
            for symptom in results["extracted_symptoms"]
        ])
        st.markdown(symptoms_html, unsafe_allow_html=True)
        st.markdown("")
    else:
        st.info("ℹ️ No symptoms were extracted from the input.")
    
    # Mapped symptoms
    if results.get("mapped_symptoms"):
        with st.expander("📋 Technical Details: Mapped Symptoms"):
            st.write(", ".join(results["mapped_symptoms"]))
    
    st.markdown("---")
    
    # Top predictions
    st.markdown("### 🏥 Top 3 Predicted Conditions")
    
    predictions = results.get("top_predictions", [])
    if predictions:
        for i, pred in enumerate(predictions, 1):
            probability_pct = pred["probability"] * 100
            
            st.markdown(f"""
            <div class="prediction-card">
                <strong style="font-size: 1.1rem;">{i}. {pred['disease']}</strong><br>
                <span style="color: #666;">Probability: {probability_pct:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(pred["probability"])
            st.markdown("")
    else:
        st.warning("⚠️ No predictions available.")
    
    st.markdown("---")
    
    # Risk assessment
    risk_level = results.get("risk_level", "Unknown")
    confidence_level = results.get("confidence_level", "Unknown")
    referral = results.get("referral_recommendation", "")
    
    risk_class = f"risk-{risk_level.lower()}"
    risk_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(risk_level, "⚪")
    
    st.markdown(f"### {risk_emoji} Risk Assessment")
    
    st.markdown(f"""
    <div class="{risk_class}">
        <strong style="font-size: 1.3rem;">Risk Level: {risk_level}</strong><br>
        <strong style="font-size: 1.1rem;">Confidence: {confidence_level}</strong><br>
        <br>
        <strong style="font-size: 1.1rem;">📍 Recommendation:</strong><br>
        <span style="font-size: 1.2rem;">{referral}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if confidence_level == "Low":
        st.warning("⚠️ **Low Confidence Warning**: Limited symptoms provided. Please seek professional medical advice.")
    
    st.success("✅ Analysis complete! Please follow the recommendation above.")


def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="main-header">🏥 SwasthyaAI Lite</div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Rural Health Screening System</p>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ Important Disclaimer:</strong><br>
        This is a screening tool only. <strong>Not a substitute for professional medical diagnosis.</strong>
        Always consult with qualified healthcare professionals for medical advice and treatment.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    bedrock_extractor, symptom_mapper, ml_predictor, risk_engine, error = initialize_components()
    
    if error:
        st.error(f"❌ Failed to initialize system: {error}")
        st.info("💡 Make sure model files exist in the 'models' directory. Run training script if needed.")
        return
    
    # Symptom input
    st.markdown("### 📝 Describe Patient Symptoms")
    st.markdown("Enter symptoms in Hindi, English, or mixed languages")
    
    text_input = st.text_area(
        "",
        placeholder="Example:\n• Patient has fever, headache, and body pain for 3 days\n• मरीज को बुखार, सिर दर्द और शरीर में दर्द है\n• Patient ko bukhar aur headache hai",
        height=150,
        max_chars=1000,
        help="Describe all symptoms the patient is experiencing"
    )
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button("🔍 Analyze Symptoms", key="analyze_btn")
    
    # Process analysis
    if submit_button:
        if not text_input or not text_input.strip():
            st.error("❌ Please describe the patient symptoms before analyzing.")
        else:
            with st.spinner("🔄 Analyzing symptoms... Please wait..."):
                results = analyze_symptoms_local(
                    text_input,
                    bedrock_extractor,
                    symptom_mapper,
                    ml_predictor,
                    risk_engine
                )
            
            if results:
                display_results(results)
            else:
                st.error("❌ Analysis failed. Please try again.")


def show_sidebar():
    """Show sidebar with information."""
    with st.sidebar:
        st.markdown("## ℹ️ About")
        st.markdown("""
        **SwasthyaAI Lite** is an AI-powered health screening tool designed for ASHA workers in rural India.
        
        ### Features:
        - 🌐 Multi-language support (Hindi/English)
        - 🤖 AI-powered symptom extraction
        - 🏥 Disease prediction
        - ⚠️ Risk assessment
        - 📍 Referral guidance
        
        ### How to Use:
        1. Describe patient symptoms in the text box
        2. Click "Analyze Symptoms"
        3. Review the predictions and risk level
        4. Follow the referral recommendation
        
        ### Version: 1.0.0
        """)
        
        st.markdown("---")
        st.markdown("## 📞 Support")
        st.markdown("""
        For technical support:
        - Contact your PHC coordinator
        - Report issues to system admin
        """)


# Show sidebar
show_sidebar()

# Run main app
if __name__ == "__main__":
    main()
