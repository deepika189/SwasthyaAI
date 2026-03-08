@echo off
echo ========================================
echo SwasthyaAI Lite - Starting Application
echo ========================================
echo.

REM Set environment variable for mock Bedrock
set USE_MOCK_BEDROCK=true

echo [1/2] Starting FastAPI Backend...
echo.
start "SwasthyaAI Backend" cmd /k "python start_backend.py"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Starting Streamlit UI...
echo.
start "SwasthyaAI UI" cmd /k "python start_ui.py"

echo.
echo ========================================
echo Application Started Successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Streamlit UI: http://localhost:8501
echo.
echo The UI will open automatically in a few seconds...
echo.

timeout /t 8 /nobreak > nul
start http://localhost:8501

echo.
echo To stop the application:
echo - Close both terminal windows
echo   OR
echo - Press Ctrl+C in each window
echo.
pause
