"""
PDF processing module for extracting and chunking text from Ayurvedic remedies PDF.
"""

import logging
from typing import List
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Raised when PDF processing fails."""
    pass


class PDFProcessor:
    """Processes PDF documents and splits them into semantic chunks."""
    
    def __init__(self, pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200, max_chunks: int = None):
        """
        Initialize PDF processor with chunking parameters.
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            max_chunks: Maximum number of chunks to return (None for all chunks)
        """
        self.pdf_path = pdf_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunks = max_chunks
        
        logger.info(f"PDFProcessor initialized: path={pdf_path}, chunk_size={chunk_size}, overlap={chunk_overlap}, max_chunks={max_chunks}")
    
    def load_and_chunk(self) -> List[dict]:
        """
        Load PDF and split into chunks.
        
        Returns:
            List of document chunks with text and metadata
            
        Raises:
            PDFProcessingError: If PDF cannot be loaded or processed
        """
        try:
            # Check if PDF file exists
            if not os.path.exists(self.pdf_path):
                raise PDFProcessingError(f"PDF file not found: {self.pdf_path}")
            
            logger.info(f"Loading PDF from: {self.pdf_path}")
            
            # Import pypdf for PDF extraction
            try:
                from pypdf import PdfReader
            except ImportError:
                raise PDFProcessingError("pypdf library not installed. Run: pip install pypdf")
            
            # Load PDF and extract text
            reader = PdfReader(self.pdf_path)
            total_pages = len(reader.pages)
            logger.info(f"PDF loaded successfully: {total_pages} pages")
            
            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        full_text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not full_text.strip():
                raise PDFProcessingError("No text content extracted from PDF")
            
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            
            # Import LangChain for text splitting
            try:
                from langchain_text_splitters import RecursiveCharacterTextSplitter
            except ImportError:
                raise PDFProcessingError("langchain-text-splitters library not installed. Run: pip install langchain-text-splitters")
            
            # Create text splitter with configured parameters
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            # Split text into chunks
            chunks = text_splitter.split_text(full_text)
            logger.info(f"Split text into {len(chunks)} chunks")
            
            # Limit chunks if max_chunks is specified
            if self.max_chunks and len(chunks) > self.max_chunks:
                logger.info(f"Limiting to first {self.max_chunks} chunks (out of {len(chunks)})")
                chunks = chunks[:self.max_chunks]
            
            # Create document objects with metadata
            documents = []
            for i, chunk_text in enumerate(chunks):
                doc = {
                    "page_content": chunk_text,
                    "metadata": {
                        "source": self.pdf_path,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                }
                documents.append(doc)
            
            logger.info(f"Created {len(documents)} document chunks")
            return documents
            
        except PDFProcessingError:
            raise
        except Exception as e:
            logger.error(f"PDF processing failed: {e}", exc_info=True)
            raise PDFProcessingError(f"Failed to process PDF: {str(e)}")
