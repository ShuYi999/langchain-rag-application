#!/usr/bin/env powershell
# Quick Start Script for RAG Application
# Run this script to quickly start the entire application

Write-Host "🚀 RAG Application Quick Start" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists and is complete
if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    if (Test-Path "venv") {
        Write-Host "⚠️  Incomplete virtual environment detected, removing..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv
    }
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created`n" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment exists`n" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated`n" -ForegroundColor Green

# Check if dependencies are installed
Write-Host "📚 Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list 2>&1 | Out-String
if ($pipList -notmatch "fastapi" -or $pipList -notmatch "streamlit") {
    Write-Host "📥 Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    pip install -r requirements_frontend.txt
    Write-Host "✅ Dependencies installed`n" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies already installed`n" -ForegroundColor Green
}

# Check if Ollama is running
Write-Host "🤖 Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaCheck = ollama list 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Ollama is installed" -ForegroundColor Green
        
        # Check if model exists
        if ($ollamaCheck -match "llama3.2:1b") {
            Write-Host "✅ llama3.2:1b model is available`n" -ForegroundColor Green
        } else {
            Write-Host "⚠️  llama3.2:1b model not found" -ForegroundColor Yellow
            Write-Host "📥 Pulling model (this will take a few minutes)..." -ForegroundColor Yellow
            ollama pull llama3.2:1b
            Write-Host "✅ Model pulled successfully`n" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "❌ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
    Write-Host "After installing, run: ollama pull llama3.2:1b`n" -ForegroundColor Yellow
    exit 1
}

# Check if documents folder exists
if (-Not (Test-Path "documents")) {
    Write-Host "📁 Creating documents folder..." -ForegroundColor Yellow
    mkdir documents
    Write-Host "⚠️  Please add .txt files to the documents/ folder`n" -ForegroundColor Yellow
} else {
    $txtFiles = Get-ChildItem -Path "documents" -Filter "*.txt"
    if ($txtFiles.Count -eq 0) {
        Write-Host "⚠️  No .txt files found in documents/ folder" -ForegroundColor Yellow
        Write-Host "Please add your document files before starting the application`n" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Found $($txtFiles.Count) document(s) in documents/ folder`n" -ForegroundColor Green
    }
}

# Start services
Write-Host "`n📋 Choose how to start the application:" -ForegroundColor Cyan
Write-Host "1. Start API only (port 8000)" -ForegroundColor White
Write-Host "2. Start Frontend only (port 8501)" -ForegroundColor White
Write-Host "3. Start both API and Frontend" -ForegroundColor White
Write-Host "4. Run evaluation script" -ForegroundColor White
Write-Host "5. Exit" -ForegroundColor White

$choice = Read-Host "`nEnter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`n🚀 Starting FastAPI server..." -ForegroundColor Green
        Write-Host "API will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
        Write-Host "API Docs: http://127.0.0.1:8000/docs`n" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop (may need to press twice)`n" -ForegroundColor Gray
        uvicorn RAG_API:app --host 127.0.0.1 --port 8000
    }
    "2" {
        Write-Host "`n🚀 Starting Streamlit frontend..." -ForegroundColor Green
        Write-Host "Frontend will be available at: http://localhost:8501`n" -ForegroundColor Cyan
        Write-Host "⚠️  Make sure the API is running on port 8000!`n" -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray
        streamlit run RAG_Frontend.py
    }
    "3" {
        Write-Host "`n🚀 Starting both services..." -ForegroundColor Green
        Write-Host "API: http://127.0.0.1:8000" -ForegroundColor Cyan
        Write-Host "Frontend: http://localhost:8501`n" -ForegroundColor Cyan
        
        # Start API in background
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; Write-Host 'API Server - Press Ctrl+C to stop' -ForegroundColor Yellow; uvicorn RAG_API:app --host 127.0.0.1 --port 8000"
        
        # Wait a bit for API to start
        Start-Sleep -Seconds 3
        
        # Start Frontend
        Write-Host "Press Ctrl+C to stop frontend`n" -ForegroundColor Gray
        streamlit run RAG_Frontend.py
    }
    "4" {
        Write-Host "`n🔬 Running evaluation script..." -ForegroundColor Green
        python RAG_Evaluation.py
    }
    "5" {
        Write-Host "`n👋 Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "`n❌ Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}
