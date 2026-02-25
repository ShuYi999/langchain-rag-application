@echo off
echo ========================================
echo Starting RAG API Server
echo ========================================
echo.
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo Starting uvicorn on http://localhost:8000...
echo.
uvicorn RAG_API:app --host 127.0.0.1 --port 8000
pause
