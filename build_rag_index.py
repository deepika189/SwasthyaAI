"""
Script to build FAISS index slowly to avoid AWS throttling.
Run this once to create the index, then the API can load it.
"""

import os
import time
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def build_index_slowly():
    """Build FAISS index with very slow rate to avoid throttling."""
    
    from app.pdf_processor import PDFProcessor
    from app.bedrock_embeddings import BedrockEmbeddingsWrapper
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    
    # Configuration
    pdf_path = os.getenv("RAG_PDF_PATH", "data/The complete book of Ayurvedic home remedies.pdf")
    index_path = os.getenv("RAG_INDEX_PATH", "data/faiss_index")
    max_chunks = int(os.getenv("RAG_MAX_CHUNKS", "100"))
    region = os.getenv("AWS_REGION", "us-east-1")
    embeddings_model = os.getenv("RAG_EMBEDDINGS_MODEL", "amazon.titan-embed-text-v2:0")
    
    logger.info("=" * 60)
    logger.info("BUILDING FAISS INDEX SLOWLY")
    logger.info("=" * 60)
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Max chunks: {max_chunks}")
    logger.info(f"Index path: {index_path}")
    logger.info(f"Embeddings model: {embeddings_model}")
    logger.info("=" * 60)
    
    # Process PDF
    logger.info("Step 1: Processing PDF...")
    processor = PDFProcessor(pdf_path, max_chunks=max_chunks)
    chunks = processor.load_and_chunk()
    logger.info(f"Extracted {len(chunks)} chunks")
    
    # Convert to documents
    documents = []
    for chunk in chunks:
        doc = Document(
            page_content=chunk["page_content"],
            metadata=chunk["metadata"]
        )
        documents.append(doc)
    
    # Initialize embeddings with VERY slow settings
    logger.info("Step 2: Initializing embeddings...")
    embeddings = BedrockEmbeddingsWrapper(
        model_id=embeddings_model,
        region=region
    )
    # Override with even slower settings
    embeddings.batch_size = 1  # Process 1 at a time
    embeddings.batch_delay = 10  # Wait 10 seconds between each
    embeddings.max_retries = 5
    
    logger.info(f"Settings: batch_size=1, delay=10s, retries=5")
    logger.info(f"Estimated time: {len(documents) * 15 / 60:.1f} minutes")
    logger.info("=" * 60)
    
    # Build index
    logger.info("Step 3: Building FAISS index (this will take a while)...")
    logger.info("You can monitor progress in the logs...")
    
    try:
        vector_store = FAISS.from_documents(
            documents,
            embeddings
        )
        
        # Save index
        logger.info("Step 4: Saving index...")
        os.makedirs(index_path, exist_ok=True)
        vector_store.save_local(index_path)
        
        logger.info("=" * 60)
        logger.info("✓ INDEX BUILT SUCCESSFULLY!")
        logger.info(f"✓ Saved to: {index_path}")
        logger.info("✓ You can now enable RAG in .env and restart the API")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to build index: {e}")
        logger.error("Try again later or request AWS quota increase")
        raise

if __name__ == "__main__":
    try:
        build_index_slowly()
    except KeyboardInterrupt:
        logger.info("\nBuild cancelled by user")
    except Exception as e:
        logger.error(f"Build failed: {e}")
        exit(1)
