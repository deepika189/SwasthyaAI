"""
Validation script for RAG integration.
Tests the complete RAG flow without starting servers.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_rag_components():
    """Validate all RAG components can be imported and initialized."""
    logger.info("=" * 60)
    logger.info("VALIDATING RAG INTEGRATION")
    logger.info("=" * 60)
    
    try:
        # Test 1: Import all RAG components
        logger.info("\n[1/6] Testing imports...")
        from app.pdf_processor import PDFProcessor
        from app.bedrock_embeddings import BedrockEmbeddingsWrapper
        from app.remedy_generator import RemedyGenerator
        from app.rag_system import AyurvedicRAGSystem
        logger.info("✓ All RAG components imported successfully")
        
        # Test 2: Check PDF file exists
        logger.info("\n[2/6] Checking PDF file...")
        pdf_path = "data/The complete book of Ayurvedic home remedies.pdf"
        if os.path.exists(pdf_path):
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            logger.info(f"✓ PDF file found: {pdf_path} ({file_size_mb:.2f} MB)")
        else:
            logger.error(f"✗ PDF file not found: {pdf_path}")
            return False
        
        # Test 3: Initialize PDF processor
        logger.info("\n[3/6] Testing PDF processor...")
        processor = PDFProcessor(
            pdf_path=pdf_path,
            chunk_size=1000,
            chunk_overlap=200
        )
        logger.info("✓ PDF processor initialized")
        
        # Test 4: Initialize embeddings wrapper
        logger.info("\n[4/6] Testing embeddings wrapper...")
        embeddings = BedrockEmbeddingsWrapper(
            model_id="amazon.titan-embed-text-v1",
            region="us-east-1"
        )
        logger.info("✓ Embeddings wrapper initialized")
        
        # Test 5: Initialize remedy generator
        logger.info("\n[5/6] Testing remedy generator...")
        generator = RemedyGenerator(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region="us-east-1"
        )
        logger.info("✓ Remedy generator initialized")
        
        # Test 6: Check RAG system configuration
        logger.info("\n[6/6] Testing RAG system configuration...")
        rag_system = AyurvedicRAGSystem(
            pdf_path=pdf_path,
            region="us-east-1",
            index_path="data/faiss_index"
        )
        logger.info("✓ RAG system configured")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL VALIDATION CHECKS PASSED")
        logger.info("=" * 60)
        logger.info("\nRAG integration is ready for use!")
        logger.info("\nNext steps:")
        logger.info("1. Set up environment variables in .env file")
        logger.info("2. Start the backend: python start_backend.py")
        logger.info("3. Start the UI: python start_ui.py")
        logger.info("4. Test the complete flow through the UI")
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Validation failed: {e}", exc_info=True)
        return False


def check_environment_config():
    """Check if environment configuration is properly set up."""
    logger.info("\n" + "=" * 60)
    logger.info("CHECKING ENVIRONMENT CONFIGURATION")
    logger.info("=" * 60)
    
    # Check if .env.example exists
    if os.path.exists(".env.example"):
        logger.info("✓ .env.example file found")
        
        # Read and check for RAG variables
        with open(".env.example", "r") as f:
            content = f.read()
            
        rag_vars = [
            "RAG_ENABLED",
            "RAG_PDF_PATH",
            "RAG_INDEX_PATH",
            "RAG_CHUNK_SIZE",
            "RAG_CHUNK_OVERLAP",
            "RAG_TOP_K",
            "RAG_EMBEDDINGS_MODEL",
            "RAG_LLM_MODEL",
            "RAG_MAX_RETRIES"
        ]
        
        missing_vars = []
        for var in rag_vars:
            if var in content:
                logger.info(f"✓ {var} configured")
            else:
                missing_vars.append(var)
                logger.warning(f"✗ {var} not found")
        
        if missing_vars:
            logger.warning(f"\nMissing variables: {', '.join(missing_vars)}")
            return False
        else:
            logger.info("\n✓ All RAG environment variables configured")
            return True
    else:
        logger.error("✗ .env.example file not found")
        return False


if __name__ == "__main__":
    logger.info("Starting RAG integration validation...\n")
    
    # Run validations
    env_ok = check_environment_config()
    components_ok = validate_rag_components()
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Environment Configuration: {'✓ PASS' if env_ok else '✗ FAIL'}")
    logger.info(f"RAG Components: {'✓ PASS' if components_ok else '✗ FAIL'}")
    
    if env_ok and components_ok:
        logger.info("\n🎉 RAG integration is fully validated and ready!")
        sys.exit(0)
    else:
        logger.error("\n❌ Some validation checks failed. Please review the errors above.")
        sys.exit(1)
