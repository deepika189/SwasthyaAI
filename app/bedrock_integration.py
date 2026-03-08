"""
Amazon Bedrock integration module for symptom extraction.
Uses LLMs to extract structured symptoms from plain-language input.
"""

import json
import logging
from typing import List, Optional
import os

logger = logging.getLogger(__name__)


class BedrockExtractionError(Exception):
    """Raised when symptom extraction fails."""
    pass


class BedrockSymptomExtractor:
    """Extracts structured symptoms from plain-language text using Amazon Bedrock."""
    
    def __init__(
        self,
        model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
        region: Optional[str] = None
    ):
        """
        Initialize Bedrock symptom extractor.
        
        Args:
            model_id: Bedrock model ID to use
            region: AWS region (defaults to AWS_REGION env var or us-east-1)
        """
        self.model_id = model_id
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.temperature = 0.0
        self.max_tokens = 200
        self.max_retries = 2
        
        # Initialize Bedrock client (lazy loading)
        self._bedrock_client = None
        
        logger.info(f"BedrockSymptomExtractor initialized with model: {model_id}")
    
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
                raise BedrockExtractionError(f"Failed to initialize Bedrock client: {e}")
        
        return self._bedrock_client
    
    def extract_symptoms(self, text_input: str) -> List[str]:
        """
        Extract symptoms from plain-language text.
        
        Args:
            text_input: Plain-language symptom description
            
        Returns:
            List of symptom strings
            
        Raises:
            BedrockExtractionError: If extraction fails after retries
        """
        if not text_input or not text_input.strip():
            logger.warning("Empty input provided")
            return []
        
        # Try extraction with retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Extraction attempt {attempt + 1}/{self.max_retries + 1}")
                
                # Build prompt
                prompt = self._build_prompt(text_input)
                
                # Call Bedrock API
                response = self._call_bedrock_api(prompt)
                
                # Parse response
                symptoms = self._parse_response(response)
                
                logger.info(f"Successfully extracted {len(symptoms)} symptoms")
                return symptoms
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries:
                    logger.error("All retry attempts exhausted")
                    return []  # Return empty list on persistent failure
                continue
                
            except Exception as e:
                logger.error(f"Extraction failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries:
                    logger.error("All retry attempts exhausted")
                    return []  # Return empty list on persistent failure
                continue
        
        return []
    
    def _build_prompt(self, text_input: str) -> str:
        """
        Build prompt with guardrails for symptom extraction.
        
        Args:
            text_input: User's symptom description
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a medical symptom extraction assistant. Your ONLY task is to extract symptom terms from patient descriptions.

CRITICAL RULES:
1. Extract ONLY symptoms (e.g., fever, cough, headache, pain, rash)
2. Do NOT provide diagnosis, medical advice, or treatment recommendations
3. Do NOT include explanations or additional text
4. Return ONLY a JSON list of symptom strings
5. Use simple, standardized medical terms in English
6. Ignore non-symptom information (age, gender, duration, etc.)
7. If input is in Hindi or mixed language, translate symptoms to English

Input: {text_input}

Output format (JSON list only):
["symptom1", "symptom2", "symptom3"]

JSON output:"""
        
        return prompt
    
    def _call_bedrock_api(self, prompt: str) -> dict:
        """
        Call Bedrock API with the prompt.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            API response dictionary
            
        Raises:
            BedrockExtractionError: If API call fails
        """
        try:
            client = self._get_bedrock_client()
            
            # Prepare request body based on model
            if "anthropic" in self.model_id.lower():
                # Claude model format
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
            elif "titan" in self.model_id.lower():
                # Titan model format
                request_body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": self.max_tokens,
                        "temperature": self.temperature,
                        "topP": 1.0
                    }
                }
            else:
                raise BedrockExtractionError(f"Unsupported model: {self.model_id}")
            
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
            raise BedrockExtractionError(f"API call failed: {e}")
    
    def _parse_response(self, response: dict) -> List[str]:
        """
        Parse and validate JSON response from Bedrock.
        
        Args:
            response: API response dictionary
            
        Returns:
            List of symptom strings
            
        Raises:
            json.JSONDecodeError: If response is not valid JSON
            BedrockExtractionError: If response format is invalid
        """
        try:
            # Extract text based on model type
            if "anthropic" in self.model_id.lower():
                # Claude response format
                if "content" in response and len(response["content"]) > 0:
                    text = response["content"][0]["text"]
                else:
                    raise BedrockExtractionError("Invalid Claude response format")
            elif "titan" in self.model_id.lower():
                # Titan response format
                if "results" in response and len(response["results"]) > 0:
                    text = response["results"][0]["outputText"]
                else:
                    raise BedrockExtractionError("Invalid Titan response format")
            else:
                raise BedrockExtractionError(f"Unsupported model: {self.model_id}")
            
            # Clean the text
            text = text.strip()
            
            # Try to find JSON array in the response
            # Look for [...] pattern
            start_idx = text.find('[')
            end_idx = text.rfind(']')
            
            if start_idx == -1 or end_idx == -1:
                logger.warning(f"No JSON array found in response: {text[:100]}")
                return []
            
            json_str = text[start_idx:end_idx + 1]
            
            # Parse JSON
            symptoms = json.loads(json_str)
            
            # Validate it's a list
            if not isinstance(symptoms, list):
                logger.warning(f"Response is not a list: {type(symptoms)}")
                return []
            
            # Filter and validate symptoms
            valid_symptoms = []
            for symptom in symptoms:
                if isinstance(symptom, str) and symptom.strip():
                    # Check for diagnosis keywords (safety check)
                    if not self._contains_diagnosis_keywords(symptom):
                        valid_symptoms.append(symptom.strip())
                    else:
                        logger.warning(f"Filtered out potential diagnosis: {symptom}")
            
            return valid_symptoms
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Response parsing failed: {e}")
            raise BedrockExtractionError(f"Failed to parse response: {e}")
    
    def _contains_diagnosis_keywords(self, text: str) -> bool:
        """
        Check if text contains diagnosis-related keywords.
        
        Args:
            text: Text to check
            
        Returns:
            True if diagnosis keywords found
        """
        diagnosis_keywords = [
            "diagnosis", "diagnose", "treatment", "prescription",
            "medication", "medicine", "cure", "therapy", "disease is"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in diagnosis_keywords)


# Mock extractor for testing without AWS credentials
class MockBedrockSymptomExtractor:
    """Mock extractor for testing without AWS credentials."""
    
    def __init__(self, model_id: str = "mock", region: Optional[str] = None):
        """Initialize mock extractor."""
        self.model_id = model_id
        self.region = region
        logger.info("MockBedrockSymptomExtractor initialized (no AWS required)")
    
    def extract_symptoms(self, text_input: str) -> List[str]:
        """
        Mock symptom extraction using simple keyword matching.
        
        Args:
            text_input: Plain-language symptom description
            
        Returns:
            List of symptom strings
        """
        if not text_input or not text_input.strip():
            return []
        
        # Simple keyword-based extraction for testing
        text_lower = text_input.lower()
        
        symptom_keywords = {
            "fever": "high_fever",
            "bukhar": "high_fever",
            "headache": "headache",
            "sir dard": "headache",
            "cough": "cough",
            "khansi": "cough",
            "pain": "pain",
            "dard": "pain",
            "fatigue": "fatigue",
            "tired": "fatigue",
            "chills": "chills",
            "itching": "itching",
            "khujli": "itching",
            "rash": "skin_rash",
            "vomiting": "vomiting",
            "ulti": "vomiting",
            "nausea": "nausea",
            "dizziness": "dizziness",
            "chakkar": "dizziness",
        }
        
        extracted = []
        for keyword, symptom in symptom_keywords.items():
            if keyword in text_lower and symptom not in extracted:
                extracted.append(symptom)
        
        logger.info(f"Mock extracted {len(extracted)} symptoms")
        return extracted
