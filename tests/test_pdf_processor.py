"""
Unit tests for PDF processor module.
"""

import pytest
import os
from app.pdf_processor import PDFProcessor, PDFProcessingError


class TestPDFProcessor:
    """Test suite for PDFProcessor class."""
    
    def test_initialization(self):
        """Test PDFProcessor initialization with default parameters."""
        processor = PDFProcessor("data/test.pdf")
        assert processor.pdf_path == "data/test.pdf"
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200
    
    def test_initialization_custom_params(self):
        """Test PDFProcessor initialization with custom parameters."""
        processor = PDFProcessor("data/test.pdf", chunk_size=500, chunk_overlap=100)
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 100
    
    def test_load_and_chunk_missing_file(self):
        """Test that missing PDF file raises PDFProcessingError."""
        processor = PDFProcessor("nonexistent.pdf")
        with pytest.raises(PDFProcessingError, match="PDF file not found"):
            processor.load_and_chunk()
    
    def test_load_and_chunk_with_real_pdf(self):
        """Test loading and chunking with the actual Ayurvedic remedies PDF."""
        pdf_path = "data/The complete book of Ayurvedic home remedies.pdf"
        
        # Skip test if PDF doesn't exist
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF file not found: {pdf_path}")
        
        processor = PDFProcessor(pdf_path, chunk_size=1000, chunk_overlap=200)
        documents = processor.load_and_chunk()
        
        # Validate results
        assert len(documents) > 0, "Should extract at least one chunk"
        
        # Check first document structure
        first_doc = documents[0]
        assert "page_content" in first_doc
        assert "metadata" in first_doc
        assert isinstance(first_doc["page_content"], str)
        assert len(first_doc["page_content"]) > 0
        
        # Check metadata
        metadata = first_doc["metadata"]
        assert "source" in metadata
        assert "chunk_id" in metadata
        assert "total_chunks" in metadata
        assert metadata["source"] == pdf_path
        assert metadata["chunk_id"] == 0
        assert metadata["total_chunks"] == len(documents)
        
        # Validate chunk sizes are reasonable
        for doc in documents:
            chunk_len = len(doc["page_content"])
            # Chunks should be roughly chunk_size, allowing for overlap and splitting
            assert chunk_len <= 1500, f"Chunk too large: {chunk_len} chars"
