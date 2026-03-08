"""
Unit tests for RAG system module.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from app.rag_system import AyurvedicRAGSystem, RAGInitializationError, RAGQueryError


class TestAyurvedicRAGSystem:
    """Test suite for AyurvedicRAGSystem class."""
    
    def test_initialization(self):
        """Test RAG system initialization with default parameters."""
        rag = AyurvedicRAGSystem(pdf_path="data/test.pdf")
        assert rag.pdf_path == "data/test.pdf"
        assert rag.embeddings_model_id == "amazon.titan-embed-text-v1"
        assert rag.llm_model_id == "anthropic.claude-3-haiku-20240307-v1:0"
        assert rag.top_k == 3
    
    def test_initialization_custom_params(self):
        """Test RAG system initialization with custom parameters."""
        rag = AyurvedicRAGSystem(
            pdf_path="data/test.pdf",
            top_k=5,
            index_path="custom/path"
        )
        assert rag.top_k == 5
        assert rag.index_path == "custom/path"
    
    def test_get_remedies_empty_query(self):
        """Test that empty query returns appropriate message."""
        rag = AyurvedicRAGSystem(pdf_path="data/test.pdf")
        # Don't initialize, just test the method
        result = rag.get_remedies("")
        assert "Please provide symptom description" in result
    
    @patch('app.pdf_processor.PDFProcessor')
    @patch('app.bedrock_embeddings.BedrockEmbeddingsWrapper')
    @patch('app.remedy_generator.RemedyGenerator')
    @patch('langchain_community.vectorstores.FAISS')
    def test_initialize_builds_new_index(self, mock_faiss, mock_remedy_gen, mock_embeddings, mock_pdf_proc):
        """Test initialization builds new index when none exists."""
        # Mock PDF processor
        mock_processor = Mock()
        mock_processor.load_and_chunk.return_value = [
            {"page_content": "Test content", "metadata": {"source": "test.pdf", "chunk_id": 0}}
        ]
        mock_pdf_proc.return_value = mock_processor
        
        # Mock embeddings
        mock_embeddings.return_value = Mock()
        
        # Mock remedy generator
        mock_remedy_gen.return_value = Mock()
        
        # Mock FAISS
        mock_vector_store = Mock()
        mock_vector_store.index.ntotal = 1
        mock_faiss.from_documents.return_value = mock_vector_store
        
        rag = AyurvedicRAGSystem(pdf_path="data/test.pdf", index_path="test_index")
        
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs'):
                rag.initialize()
        
        assert rag.vector_store is not None
        assert mock_pdf_proc.called
        assert mock_faiss.from_documents.called
    
    @patch('app.bedrock_embeddings.BedrockEmbeddingsWrapper')
    @patch('app.remedy_generator.RemedyGenerator')
    @patch('langchain_community.vectorstores.FAISS')
    def test_initialize_loads_existing_index(self, mock_faiss, mock_remedy_gen, mock_embeddings):
        """Test initialization loads existing index when available."""
        # Mock embeddings
        mock_embeddings.return_value = Mock()
        
        # Mock remedy generator
        mock_remedy_gen.return_value = Mock()
        
        # Mock FAISS load
        mock_vector_store = Mock()
        mock_vector_store.index.ntotal = 10
        mock_faiss.load_local.return_value = mock_vector_store
        
        rag = AyurvedicRAGSystem(pdf_path="data/test.pdf", index_path="test_index")
        
        with patch('os.path.exists', return_value=True):
            rag.initialize()
        
        assert rag.vector_store is not None
        assert mock_faiss.load_local.called
    
    def test_get_remedies_without_initialization(self):
        """Test get_remedies handles uninitialized state gracefully."""
        rag = AyurvedicRAGSystem(pdf_path="data/test.pdf")
        result = rag.get_remedies("fever and headache")
        
        # Should return error message, not crash
        assert "No relevant" in result or "temporarily unavailable" in result
    
    @patch('app.bedrock_embeddings.BedrockEmbeddingsWrapper')
    @patch('app.remedy_generator.RemedyGenerator')
    @patch('langchain_community.vectorstores.FAISS')
    def test_get_remedies_success(self, mock_faiss, mock_remedy_gen, mock_embeddings):
        """Test successful remedy retrieval and generation."""
        # Mock components
        mock_embeddings.return_value = Mock()
        
        mock_generator = Mock()
        mock_generator.generate.return_value = "1. Drink ginger tea\n2. Get rest"
        mock_remedy_gen.return_value = mock_generator
        
        # Mock vector store
        mock_doc = Mock()
        mock_doc.page_content = "Ginger is good for fever"
        mock_vector_store = Mock()
        mock_vector_store.similarity_search.return_value = [mock_doc]
        mock_vector_store.index.ntotal = 1
        mock_faiss.load_local.return_value = mock_vector_store
        
        rag = AyurvedicRAGSystem(pdf_path="data/test.pdf")
        
        with patch('os.path.exists', return_value=True):
            rag.initialize()
        
        result = rag.get_remedies("fever and headache")
        
        assert "ginger tea" in result.lower()
        assert mock_vector_store.similarity_search.called
        assert mock_generator.generate.called
