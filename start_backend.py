"""
Script to start the FastAPI backend with proper configuration.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set environment variables (override if needed)
if not os.getenv("USE_MOCK_BEDROCK"):
    os.environ["USE_MOCK_BEDROCK"] = "false"  # Use real Bedrock by default
if not os.getenv("RAG_ENABLED"):
    os.environ["RAG_ENABLED"] = "true"  # Enable RAG by default

# Start uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
