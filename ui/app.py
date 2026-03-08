"""
Streamlit UI for SwasthyaAI Lite.
Simple interface for ASHA workers to input symptoms and view results.
"""

import streamlit as st
import requests
import os

# Page configuration
st.set_page_config(
    page_title="SwasthyaAI Lite",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS for styling
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
    
    # Patient Information Section
    st.markdown("### 📝 Describe Patient Symptoms")
    st.markdown("Enter symptoms in Hindi, English, or mixed languages")
    
    # Symptom input
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
    
    # Process analysis when button is clicked
    if submit_button:
        if not text_input or not text_input.strip():
            st.error("❌ Please describe the patient symptoms before analyzing.")
        else:
            with st.spinner("🔄 Analyzing symptoms... Please wait..."):
                results = analyze_symptoms(text_input=text_input)
            
            if results:
                display_results(results)
            else:
                st.error("❌ Analysis failed. Please check if the API server is running at http://localhost:8000")


def analyze_symptoms(text_input: str):
    """
    Call the API to analyze symptoms.
    
    Args:
        text_input: Symptom description
        
    Returns:
        Analysis results or None if failed
    """
    try:
        # Prepare request payload
        payload = {
            "text_input": text_input
        }
        
        # Call API
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            if response.text:
                st.error(f"Details: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure the backend is running at http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def display_results(results: dict):
    """
    Display analysis results.
    
    Args:
        results: Analysis results from API
    """
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
    
    # Mapped symptoms (technical details in expander)
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
            
            # Create progress bar for visual representation
            st.markdown(f"""
            <div class="prediction-card">
                <strong style="font-size: 1.1rem;">{i}. {pred['disease']}</strong><br>
                <span style="color: #666;">Probability: {probability_pct:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Add progress bar
            st.progress(pred["probability"])
            st.markdown("")
    else:
        st.warning("⚠️ No predictions available.")
    
    st.markdown("---")
    
    # Risk assessment
    risk_level = results.get("risk_level", "Unknown")
    confidence_level = results.get("confidence_level", "Unknown")
    referral = results.get("referral_recommendation", "")
    
    # Display risk with color coding
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
    
    # Additional warning for low confidence
    if confidence_level == "Low":
        st.warning("⚠️ **Low Confidence Warning**: Limited symptoms provided. Please seek professional medical advice for accurate assessment.")
    
    # Display Ayurvedic remedies section
    if results.get("ayurvedic_remedies"):
        st.markdown("---")
        st.markdown("### 🌿 Ayurvedic Home Remedies")
        
        st.markdown("""
        <div class="disclaimer">
            <strong>ℹ️ Supplementary Information:</strong><br>
            These are traditional Ayurvedic suggestions for home care. 
            They complement but do not replace medical treatment.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(results["ayurvedic_remedies"])
        st.markdown("")
    
    # Success message
    st.success("✅ Analysis complete! Please follow the recommendation above.")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Analyze Another Patient", key="reset_btn"):
            st.experimental_rerun()
    with col2:
        if st.button("📄 Print Results", key="print_btn"):
            st.info("💡 Use your browser's print function (Ctrl+P) to print these results.")


def show_sidebar():
    """Show sidebar with additional information."""
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
        
        st.markdown("---")
        
        # API Status Check
        st.markdown("## 🔌 System Status")
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ Backend: Connected")
            else:
                st.error("❌ Backend: Error")
        except:
            st.error("❌ Backend: Disconnected")


# Show sidebar
show_sidebar()

# Run main app
if __name__ == "__main__":
    main()
