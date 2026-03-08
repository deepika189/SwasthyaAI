"""
Remedy generator module for creating Ayurvedic remedy recommendations using LLM.
"""

import logging
from typing import List, Optional
import os
import json
import time

logger = logging.getLogger(__name__)


class RemedyGenerationError(Exception):
    """Raised when remedy generation fails."""
    pass


class RemedyGenerator:
    """Generates Ayurvedic remedy recommendations using Bedrock LLM."""
    
    def __init__(
        self,
        model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
        region: Optional[str] = None,
        max_retries: int = 2
    ):
        """
        Initialize remedy generator with Bedrock LLM.
        
        Args:
            model_id: Bedrock model ID to use
            region: AWS region
            max_retries: Maximum number of retry attempts
        """
        self.model_id = model_id
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.max_retries = max_retries
        self.temperature = 0.3
        self.max_tokens = 500
        self._bedrock_client = None
        
        logger.info(f"RemedyGenerator initialized: model={model_id}, region={self.region}")
    
    def _get_bedrock_client(self):
        """Get or create Bedrock runtime client."""
        if self._bedrock_client is None:
            try:
                import boto3
                self._bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.region
                )
                logger.info(f"Bedrock client initialized for region: {self.region}")
            except Exception as e:
                raise RemedyGenerationError(f"Failed to initialize Bedrock client: {e}")
        
        return self._bedrock_client
    
    def generate(self, symptom_query: str, context_chunks: List[str]) -> str:
        """
        Generate remedy recommendations from context.
        
        Args:
            symptom_query: User's symptom description
            context_chunks: Retrieved text chunks from Ayurvedic book
            
        Returns:
            Formatted remedy recommendations
        """
        if not symptom_query or not symptom_query.strip():
            logger.warning("Empty symptom query provided")
            return "Unable to generate remedies: No symptoms provided."
        
        if not context_chunks:
            logger.warning("No context chunks provided")
            return "No relevant Ayurvedic remedies found for these symptoms."
        
        logger.info(f"Generating remedies for query with {len(context_chunks)} context chunks")
        
        # Try generation with retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Generation attempt {attempt + 1}/{self.max_retries + 1}")
                
                # Build prompt
                prompt = self._build_prompt(symptom_query, context_chunks)
                
                # Call Bedrock API
                response = self._call_bedrock_api(prompt)
                
                # Extract remedy text from response
                remedy_text = self._extract_remedy_text(response)
                
                logger.info(f"Successfully generated remedies ({len(remedy_text)} characters)")
                return remedy_text
                
            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("All retry attempts exhausted")
                    return "Unable to generate Ayurvedic remedies at this time. Please try again later."
        
        return "Unable to generate Ayurvedic remedies at this time. Please try again later."
    
    def _build_prompt(self, symptom_query: str, context_chunks: List[str]) -> str:
        """
        Build prompt with guardrails for remedy generation.
        
        Args:
            symptom_query: User's symptom description
            context_chunks: Retrieved text chunks
            
        Returns:
            Formatted prompt string
        """
        # Combine context chunks
        context_text = "\n\n".join(context_chunks[:3])  # Use top 3 chunks
        
        prompt = f"""You are an Ayurvedic health advisor. Based on the following symptom description and relevant excerpts from "The complete book of Ayurvedic home remedies", provide 3-5 practical home remedy recommendations.

SYMPTOM DESCRIPTION:
{symptom_query}

RELEVANT AYURVEDIC KNOWLEDGE:
{context_text}

INSTRUCTIONS:
1. Suggest only home remedies that are safe and practical
2. Focus on remedies mentioned in the provided context
3. Do NOT provide medical diagnosis or treatment advice
4. Format as a numbered list
5. Keep recommendations clear and concise
6. Mention any important precautions
7. If the context doesn't contain relevant remedies, say so

AYURVEDIC HOME REMEDIES:"""
        
        logger.debug(f"Built prompt with {len(prompt)} characters")
        return prompt
    
    def _call_bedrock_api(self, prompt: str) -> dict:
        """
        Call Bedrock API with the prompt.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            API response dictionary
            
        Raises:
            RemedyGenerationError: If API call fails
        """
        try:
            client = self._get_bedrock_client()
            
            # Prepare request body for Claude model
            if "anthropic" in self.model_id.lower():
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            else:
                raise RemedyGenerationError(f"Unsupported model: {self.model_id}")
            
            # Call API
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            return response_body
            
        except Exception as e:
            logger.error(f"Bedrock API call failed: {e}")
            raise RemedyGenerationError(f"API call failed: {e}")
    
    def _extract_remedy_text(self, response: dict) -> str:
        """
        Extract remedy text from Bedrock response.
        
        Args:
            response: API response dictionary
            
        Returns:
            Remedy text string
            
        Raises:
            RemedyGenerationError: If response format is invalid
        """
        try:
            # Extract text from Claude response format
            if "content" in response and len(response["content"]) > 0:
                text = response["content"][0]["text"]
                return text.strip()
            else:
                raise RemedyGenerationError("Invalid response format")
                
        except Exception as e:
            logger.error(f"Failed to extract remedy text: {e}")
            raise RemedyGenerationError(f"Failed to extract remedy text: {e}")
