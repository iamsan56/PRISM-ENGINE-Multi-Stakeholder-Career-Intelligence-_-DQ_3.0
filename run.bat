@echo off
echo ===================================================
echo     Starting PRISM Engine (DataQuest 3.0)
echo ===================================================

echo Starting FastAPI Backend...
start "PRISM API" cmd /k "cd api && python -m uvicorn main:app --reload --port 8000"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo Starting React Frontend...
start "PRISM Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo   Backend API is running at:  http://localhost:8000
echo   Frontend UI is running at:  http://localhost:5173
echo   Swagger Docs available at:  http://localhost:8000/docs
echo ===================================================
echo Press any key to exit this launcher...
pause >nul
