"""
Unit tests for remedy generator module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.remedy_generator import RemedyGenerator, RemedyGenerationError


class TestRemedyGenerator:
    """Test suite for RemedyGenerator class."""
    
    def test_initialization(self):
        """Test RemedyGenerator initialization with default parameters."""
        generator = RemedyGenerator()
        assert generator.model_id == "anthropic.claude-3-haiku-20240307-v1:0"
        assert generator.max_retries == 2
        assert generator.temperature == 0.3
        assert generator.max_tokens == 500
    
    def test_initialization_custom_params(self):
        """Test RemedyGenerator initialization with custom parameters."""
        generator = RemedyGenerator(
            model_id="custom-model",
            region="us-west-2",
            max_retries=3
        )
        assert generator.model_id == "custom-model"
        assert generator.region == "us-west-2"
        assert generator.max_retries == 3
    
    def test_generate_empty_query(self):
        """Test that empty query returns appropriate message."""
        generator = RemedyGenerator()
        result = generator.generate("", ["context"])
        assert "Unable to generate remedies" in result
        assert "No symptoms provided" in result
    
    def test_generate_no_context(self):
        """Test that no context returns appropriate message."""
        generator = RemedyGenerator()
        result = generator.generate("fever and headache", [])
        assert "No relevant Ayurvedic remedies found" in result
    
    def test_build_prompt_includes_query_and_context(self):
        """Test that prompt includes both symptom query and context."""
        generator = RemedyGenerator()
        symptom_query = "fever and headache"
        context_chunks = ["Remedy 1: Ginger tea", "Remedy 2: Rest"]
        
        prompt = generator._build_prompt(symptom_query, context_chunks)
        
        assert symptom_query in prompt
        assert "Remedy 1: Ginger tea" in prompt
        assert "Remedy 2: Rest" in prompt
        assert "AYURVEDIC HOME REMEDIES" in prompt
    
    @patch('boto3.client')
    def test_generate_success(self, mock_boto_client):
        """Test successful remedy generation."""
        # Mock Bedrock response
        mock_client = Mock()
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = b'{"content": [{"text": "1. Drink ginger tea\\n2. Get rest"}]}'
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        generator = RemedyGenerator()
        result = generator.generate("fever", ["Ginger is good for fever"])
        
        assert "Drink ginger tea" in result
        assert "Get rest" in result
        assert mock_client.invoke_model.called
    
    @patch('boto3.client')
    def test_retry_logic(self, mock_boto_client):
        """Test retry logic on failure."""
        # Mock Bedrock client that fails once then succeeds
        mock_client = Mock()
        mock_client.invoke_model.side_effect = [
            Exception("API Error"),
            {
                'body': MagicMock(**{
                    'read.return_value': b'{"content": [{"text": "Remedy text"}]}'
                })
            }
        ]
        mock_boto_client.return_value = mock_client
        
        generator = RemedyGenerator()
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = generator.generate("fever", ["context"])
        
        assert "Remedy text" in result
        assert mock_client.invoke_model.call_count == 2
    
    @patch('boto3.client')
    def test_max_retries_exhausted(self, mock_boto_client):
        """Test fallback message when all retries exhausted."""
        # Mock Bedrock client that always fails
        mock_client = Mock()
        mock_client.invoke_model.side_effect = Exception("API Error")
        mock_boto_client.return_value = mock_client
        
        generator = RemedyGenerator()
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = generator.generate("fever", ["context"])
        
        assert "Unable to generate Ayurvedic remedies" in result
        assert "try again later" in result
        assert mock_client.invoke_model.call_count == 3  # Initial + 2 retries
    
    def test_build_prompt_limits_context_chunks(self):
        """Test that prompt uses only top 3 context chunks."""
        generator = RemedyGenerator()
        context_chunks = [f"Chunk {i}" for i in range(10)]
        
        prompt = generator._build_prompt("fever", context_chunks)
        
        # Should include first 3 chunks
        assert "Chunk 0" in prompt
        assert "Chunk 1" in prompt
        assert "Chunk 2" in prompt
        # Should not include later chunks
        assert "Chunk 9" not in prompt
