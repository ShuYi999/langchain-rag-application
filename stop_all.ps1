# Stop all RAG application processes
Write-Host "🛑 Stopping all RAG services..." -ForegroundColor Yellow

# Stop Streamlit
Write-Host "Stopping Streamlit..." -ForegroundColor Gray
Get-Process | Where-Object { $_.ProcessName -eq "streamlit" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop uvicorn
Write-Host "Stopping API (uvicorn)..." -ForegroundColor Gray
Get-Process | Where-Object { $_.ProcessName -eq "uvicorn" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop Python processes in the LangChain venv
Write-Host "Stopping Python processes..." -ForegroundColor Gray
Get-Process | Where-Object { ($_.ProcessName -eq "python") -and ($_.Path -like "*LangChain*venv*") } | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 1

# Verify everything stopped
$remaining = @()
$remaining += Get-Process -Name "streamlit" -ErrorAction SilentlyContinue
$remaining += Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue

if ($remaining.Count -eq 0) {
    Write-Host "`n✅ All services stopped successfully!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some processes may still be running. Close their terminal windows manually." -ForegroundColor Yellow
}
