# PowerShell Orchestration Script for Windows Local GPU Execution
# Use this instead of docker-compose if you want native Windows CUDA Support

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Booting Local Video Dubbing Platform" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Install Requirements natively
Write-Host "[1/4] Validating local pip dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt | Out-Null

# 2. Start Uvicorn Backend (Runs on 8000)
Write-Host "[2/4] Initializing FastAPI Backend Server..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "backend.app.main:app --port 8000"

# 3. Start Celery Worker (Pool=solo for Windows compatibility)
Write-Host "[3/4] Initializing Celery Pipeline Worker..." -ForegroundColor Green
# On Windows, Celery multiprocess pool causes crashing unless set to 'solo'
$env:CELERY_BROKER_URL="redis://localhost:6379/0"
$env:CELERY_RESULT_BACKEND="redis://localhost:6379/1"
$env:OUTPUT_DIR="./storage/output"
Start-Process -NoNewWindow -FilePath "celery" -ArgumentList "-A backend.app.tasks.celery_app worker -l info -P solo"

# 4. Start Premium Gradio App (Runs on 7860)
Write-Host "[4/4] Launching OmniVoice Dubbing Studio UI..." -ForegroundColor Magenta
$env:BACKEND_URL="http://localhost:8000"
Start-Process -FilePath "python" -ArgumentList "frontend/gradio_app.py"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Local Launch Complete!" -ForegroundColor Cyan
Write-Host " 🌐 Dashboard: http://localhost:7860" -ForegroundColor White
Write-Host " 📡 API: http://localhost:8000/docs" -ForegroundColor White
Write-Host " (Ensure Redis is running locally on port 6379)" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Cyan
