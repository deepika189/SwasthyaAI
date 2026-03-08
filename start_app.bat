@echo off
echo ========================================
echo Starting SwasthyaAI Lite
echo ========================================
echo.

REM Set environment variables
set USE_MOCK_BEDROCK=true
set API_URL=http://localhost:8000

echo Starting FastAPI backend on port 8000...
start "SwasthyaAI Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Streamlit UI on port 8501...
start "SwasthyaAI UI" cmd /k "streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0"

echo.
echo ========================================
echo SwasthyaAI Lite is starting!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Streamlit UI: http://localhost:8501
echo.
echo Press any key to open the UI in your browser...
pause > nul

start http://localhost:8501

echo.
echo Application is running!
echo Close the terminal windows to stop the services.
echo.
