"""
Unit tests for Bedrock embeddings wrapper.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.bedrock_embeddings import BedrockEmbeddingsWrapper, BedrockEmbeddingsError


class TestBedrockEmbeddingsWrapper:
    """Test suite for BedrockEmbeddingsWrapper class."""
    
    def test_initialization(self):
        """Test embeddings wrapper initialization with default parameters."""
        wrapper = BedrockEmbeddingsWrapper()
        assert wrapper.model_id == "amazon.titan-embed-text-v1"
        assert wrapper.region == "us-east-1"
        assert wrapper.batch_size == 25
        assert wrapper.max_retries == 3
    
    def test_initialization_custom_params(self):
        """Test embeddings wrapper initialization with custom parameters."""
        wrapper = BedrockEmbeddingsWrapper(
            model_id="custom-model",
            region="us-west-2"
        )
        assert wrapper.model_id == "custom-model"
        assert wrapper.region == "us-west-2"
    
    def test_embed_documents_empty_list(self):
        """Test embedding empty list returns empty list."""
        wrapper = BedrockEmbeddingsWrapper()
        result = wrapper.embed_documents([])
        assert result == []
    
    @patch('boto3.client')
    def test_embed_single_text_success(self, mock_boto_client):
        """Test successful embedding generation for single text."""
        # Mock Bedrock response
        mock_client = Mock()
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = b'{"embedding": [0.1, 0.2, 0.3]}'
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        wrapper = BedrockEmbeddingsWrapper()
        embedding = wrapper.embed_query("test text")
        
        assert embedding == [0.1, 0.2, 0.3]
        assert mock_client.invoke_model.called
    
    @patch('boto3.client')
    def test_embed_documents_batching(self, mock_boto_client):
        """Test that documents are processed in batches."""
        # Mock Bedrock response
        mock_client = Mock()
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = b'{"embedding": [0.1, 0.2]}'
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        wrapper = BedrockEmbeddingsWrapper()
        texts = [f"text_{i}" for i in range(30)]  # More than batch size
        embeddings = wrapper.embed_documents(texts)
        
        assert len(embeddings) == 30
        # Should have made 30 API calls (one per text)
        assert mock_client.invoke_model.call_count == 30
    
    def test_embed_empty_text(self):
        """Test embedding empty text returns zero vector."""
        wrapper = BedrockEmbeddingsWrapper()
        embedding = wrapper._embed_single_text("")
        
        assert len(embedding) == 1536  # Titan embedding dimension
        assert all(v == 0.0 for v in embedding)
    
    @patch('boto3.client')
    def test_retry_logic_on_failure(self, mock_boto_client):
        """Test retry logic with exponential backoff."""
        # Mock Bedrock client that fails twice then succeeds
        mock_client = Mock()
        mock_client.invoke_model.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            {
                'body': MagicMock(**{
                    'read.return_value': b'{"embedding": [0.1, 0.2]}'
                })
            }
        ]
        mock_boto_client.return_value = mock_client
        
        wrapper = BedrockEmbeddingsWrapper()
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            embedding = wrapper.embed_query("test text")
        
        assert embedding == [0.1, 0.2]
        assert mock_client.invoke_model.call_count == 3
    
    @patch('boto3.client')
    def test_max_retries_exhausted(self, mock_boto_client):
        """Test that BedrockEmbeddingsError is raised after max retries."""
        # Mock Bedrock client that always fails
        mock_client = Mock()
        mock_client.invoke_model.side_effect = Exception("API Error")
        mock_boto_client.return_value = mock_client
        
        wrapper = BedrockEmbeddingsWrapper()
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(BedrockEmbeddingsError, match="Failed to generate embedding after 3 attempts"):
                wrapper.embed_query("test text")
        
        assert mock_client.invoke_model.call_count == 3
