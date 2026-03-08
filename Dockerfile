# SwasthyaAI Lite Dockerfile
# Multi-stage build for optimized image size

FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY ui/ ./ui/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY models/ ./models/
COPY .env.example .env

# Create logs directory
RUN mkdir -p logs

# Expose ports
# 8000 for FastAPI
# 8501 for Streamlit
EXPOSE 8000 8501

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "Starting SwasthyaAI Lite..."\n\
echo ""\n\
echo "Starting FastAPI backend on port 8000..."\n\
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &\n\
FASTAPI_PID=$!\n\
echo "FastAPI started with PID: $FASTAPI_PID"\n\
echo ""\n\
sleep 3\n\
echo "Starting Streamlit UI on port 8501..."\n\
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0 &\n\
STREAMLIT_PID=$!\n\
echo "Streamlit started with PID: $STREAMLIT_PID"\n\
echo ""\n\
echo "========================================"\n\
echo "SwasthyaAI Lite is running!"\n\
echo "========================================"\n\
echo "FastAPI: http://localhost:8000"\n\
echo "API Docs: http://localhost:8000/docs"\n\
echo "Streamlit UI: http://localhost:8501"\n\
echo "========================================"\n\
echo ""\n\
# Wait for both processes\n\
wait $FASTAPI_PID $STREAMLIT_PID\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
