# Hallux - Quick Start Script
# Run this to start the backend server

Write-Host "🚀 Starting Hallux Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (!(Test-Path "app")) {
    Write-Host "❌ Error: Please run this from the backend directory" -ForegroundColor Red
    Write-Host "   Run: cd backend" -ForegroundColor Yellow
    exit 1
}

# Check if venv exists
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "⚙️  Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env and add your API keys!" -ForegroundColor Red
    Write-Host "   Required: OPENAI_API_KEY or GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to edit .env now? (y/n)"
    if ($response -eq "y") {
        notepad .env
    }
}

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "💊 Health Check: http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the server
python -m app.main
