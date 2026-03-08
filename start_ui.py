"""
Script to start the Streamlit UI.
"""
import os
import sys
import subprocess

# Set environment variables
os.environ["API_URL"] = "http://localhost:8000"

# Start streamlit
if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "ui/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])
