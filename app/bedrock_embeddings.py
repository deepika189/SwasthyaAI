"""
Bedrock embeddings wrapper for generating vector embeddings using Amazon Bedrock Titan.
"""

import logging
from typing import List
import os
import json
import time

logger = logging.getLogger(__name__)


class BedrockEmbeddingsError(Exception):
    """Raised when embedding generation fails."""
    pass


class BedrockEmbeddingsWrapper:
    """Generates embeddings using Amazon Bedrock Titan Embeddings model."""
    
    def __init__(self, model_id: str = "amazon.titan-embed-text-v2:0", region: str = "us-east-1"):
        """
        Initialize Bedrock embeddings client.
        
        Args:
            model_id: Bedrock embeddings model ID (default: amazon.titan-embed-text-v2:0)
            region: AWS region
        """
        self.model_id = model_id
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self._bedrock_client = None
        self.batch_size = 5  # Small batches to avoid throttling
        self.max_retries = 3
        self.batch_delay = 5  # Longer delay between batches
        
        logger.info(f"BedrockEmbeddingsWrapper initialized: model={model_id}, region={self.region}")
    
    def _get_bedrock_client(self):
        """Get or create Bedrock runtime client."""
        if self._bedrock_client is None:
            try:
                import boto3
                self._bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.region
                )
                logger.info(f"Bedrock embeddings client initialized for region: {self.region}")
            except Exception as e:
                raise BedrockEmbeddingsError(f"Failed to initialize Bedrock client: {e}")
        
        return self._bedrock_client
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents with batching.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        logger.info(f"Embedding {len(texts)} documents in batches of {self.batch_size}")
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
            logger.info(f"Processing batch {batch_num}/{total_batches}: {len(batch)} texts")
            
            for text in batch:
                embedding = self._embed_single_text(text)
                all_embeddings.append(embedding)
            
            # Add delay between batches to avoid throttling
            if i + self.batch_size < len(texts):
                logger.debug(f"Waiting {self.batch_delay}s before next batch...")
                time.sleep(self.batch_delay)
        
        logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
        return all_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        logger.info("Embedding query text")
        return self._embed_single_text(text)
    
    def _embed_single_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text with retry logic.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            BedrockEmbeddingsError: If embedding generation fails after retries
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            # Return zero vector for empty text
            return [0.0] * 1536  # Titan embeddings dimension
        
        for attempt in range(self.max_retries):
            try:
                client = self._get_bedrock_client()
                
                # Prepare request body for Titan embeddings
                request_body = {
                    "inputText": text[:8000]  # Limit text length
                }
                
                # Call Bedrock API
                response = client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json"
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                
                # Extract embedding vector
                if "embedding" in response_body:
                    embedding = response_body["embedding"]
                    logger.debug(f"Generated embedding with dimension: {len(embedding)}")
                    return embedding
                else:
                    raise BedrockEmbeddingsError("No embedding found in response")
                
            except Exception as e:
                logger.warning(f"Embedding attempt {attempt + 1}/{self.max_retries} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff with longer delays for throttling
                    wait_time = (2 ** attempt) * 5  # Increased to 5*2^n for better throttle handling
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts exhausted for embedding generation")
                    raise BedrockEmbeddingsError(f"Failed to generate embedding after {self.max_retries} attempts: {e}")
        
        # Should never reach here
        raise BedrockEmbeddingsError("Unexpected error in embedding generation")
