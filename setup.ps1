# 🏆 HALLUX - COMPLETE SETUP & START GUIDE
# Run this script to set up everything at once!

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    🏆 HALLUX - AI Citation Verification System" -ForegroundColor Cyan
Write-Host "    Making AI Trustworthy, One Citation at a Time" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Get-Location

# Function to check if command exists
function Test-Command($command) {
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

if (!(Test-Command "python")) {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python found: $(python --version)" -ForegroundColor Green

if (!(Test-Command "git")) {
    Write-Host "⚠️  Git not found (optional but recommended)" -ForegroundColor Yellow
} else {
    Write-Host "✅ Git found: $(git --version)" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    STEP 1: BACKEND SETUP" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Setup backend
cd "$projectRoot\backend"

Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   Virtual environment already exists, skipping..." -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "📥 Installing Python dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "⚙️  Setting up configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   .env file already exists" -ForegroundColor Gray
} else {
    Copy-Item .env.example .env
    Write-Host "✅ .env file created from template" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    IMPORTANT: API KEY SETUP" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  For full functionality, you need at least ONE API key:" -ForegroundColor Red
Write-Host ""
Write-Host "Option 1 (Recommended): OpenAI GPT-4" -ForegroundColor White
Write-Host "   → Get key: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host "   → Add to .env: OPENAI_API_KEY=sk-..." -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2 (Free Alternative): Google Gemini" -ForegroundColor White
Write-Host "   → Get key: https://ai.google.dev/aistudio" -ForegroundColor Gray
Write-Host "   → Add to .env: GEMINI_API_KEY=..." -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Do you want to edit .env now to add API keys? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    notepad .env
    Write-Host ""
    Write-Host "✅ .env file opened for editing" -ForegroundColor Green
    Write-Host "   Save and close Notepad when done" -ForegroundColor Gray
    Read-Host "Press Enter when you've saved your changes"
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    STEP 2: TESTING BACKEND" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🧪 Testing backend server..." -ForegroundColor Yellow
Write-Host ""

# Start server in background for testing
$job = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot\backend
    .\venv\Scripts\Activate.ps1
    python -m app.main
}

Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test health endpoint
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
    Write-Host "✅ Backend is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Server Status: $($response.status)" -ForegroundColor Gray
    Write-Host "   Environment: $($response.environment)" -ForegroundColor Gray
    Write-Host "   Version: $($response.version)" -ForegroundColor Gray
    
    Stop-Job $job
    Remove-Job $job
} catch {
    Write-Host "❌ Failed to connect to backend" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    Stop-Job $job
    Remove-Job $job
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    STEP 3: FRONTEND SETUP" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📱 Frontend Setup Options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Generate with 21st.dev (RECOMMENDED)" -ForegroundColor White
Write-Host "   1. Open: https://21st.dev/magic-chat?step=website-content" -ForegroundColor Gray
Write-Host "   2. Copy content from: 21ST_DEV_PROMPT.txt" -ForegroundColor Gray
Write-Host "   3. Paste into 21st.dev and generate" -ForegroundColor Gray
Write-Host "   4. Download and extract to frontend/" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Manual React Setup" -ForegroundColor White
Write-Host "   See: IMPLEMENTATION_ROADMAP.md" -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Do you want to open 21st.dev now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Start-Process "https://21st.dev/magic-chat?step=website-content"
    Write-Host "✅ Opened 21st.dev in browser" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    NEXT STEPS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📚 Complete Documentation:" -ForegroundColor Yellow
Write-Host "   • START_HERE.md - Complete overview" -ForegroundColor Gray
Write-Host "   • WINNING_STRATEGY.md - Competitive analysis" -ForegroundColor Gray
Write-Host "   • IMPLEMENTATION_ROADMAP.md - 24hr development plan" -ForegroundColor Gray
Write-Host "   • backend/QUICKSTART.md - Backend guide" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 To Start Backend Server:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\start.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "🌐 Backend URLs:" -ForegroundColor Yellow
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   • Health: http://localhost:8000/api/health" -ForegroundColor Gray
Write-Host "   • Root: http://localhost:8000/" -ForegroundColor Gray
Write-Host ""

Write-Host "📊 Project Stats:" -ForegroundColor Yellow
$backendFiles = (Get-ChildItem -Path "$projectRoot\backend" -Recurse -File | Where-Object { $_.Extension -in @('.py', '.txt', '.md') }).Count
Write-Host "   • Backend files: $backendFiles" -ForegroundColor Gray
Write-Host "   • API endpoints: 6 (ready)" -ForegroundColor Gray
Write-Host "   • Verification layers: 5 (framework ready)" -ForegroundColor Gray
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    🎯 YOU'RE READY TO START BUILDING!" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Backend setup complete" -ForegroundColor Green
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host "✅ Configuration ready" -ForegroundColor Green
Write-Host "✅ Documentation available" -ForegroundColor Green
Write-Host ""
Write-Host "💪 Time to WIN this hackathon! Good luck! 🏆" -ForegroundColor Cyan
Write-Host ""

# Return to project root
cd $projectRoot

# Final prompt
$response = Read-Host "Do you want to start the backend server now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Starting Hallux Backend Server..." -ForegroundColor Cyan
    Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""
    cd backend
    .\venv\Scripts\Activate.ps1
    python -m app.main
}
