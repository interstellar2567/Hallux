# 🚀 Quick Azure Deployment Guide for Hallux

Write-Host "=================================="  -ForegroundColor Cyan
Write-Host "Azure Backend Deployment Guide" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Your existing Azure resources
$RESOURCE_GROUP = "mcve"
$APP_NAME = "Hallux"
$BACKEND_URL = "https://hallux-fefsdqc6fmbmdkcu.eastasia-01.azurewebsites.net"

Write-Host "✅ Backend already exists: $BACKEND_URL" -ForegroundColor Green
Write-Host ""

Write-Host "📝 Step-by-Step Deployment:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1️⃣  Set Environment Variables in Azure Portal" -ForegroundColor Cyan
Write-Host "   Go to: Azure Portal > Hallux > Settings > Environment variables"
Write-Host "   Add these variables:" -ForegroundColor White
Write-Host "   - OPENAI_API_KEY = your-openai-key"
Write-Host "   - GOOGLE_API_KEY = your-gemini-key"
Write-Host "   - ENV = production"
Write-Host "   - LOG_LEVEL = INFO"
Write-Host "   - ALLOWED_ORIGINS = *"
Write-Host ""

Write-Host "2️⃣  Configure Startup Command" -ForegroundColor Cyan
Write-Host "   Run this command:" -ForegroundColor White
Write-Host '   az webapp config set --name Hallux --resource-group mcve --startup-file "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"' -ForegroundColor Gray
Write-Host ""

Write-Host "3️⃣  Deploy Code via ZIP" -ForegroundColor Cyan
Write-Host "   Easiest method - ZIP deployment:" -ForegroundColor White
Write-Host "   cd backend"
Write-Host '   Compress-Archive -Path * -DestinationPath deploy.zip -Force'
Write-Host '   az webapp deployment source config-zip --resource-group mcve --name Hallux --src deploy.zip'
Write-Host ""

Write-Host "4️⃣  OR Deploy via Git" -ForegroundColor Cyan
Write-Host "   Alternative method:" -ForegroundColor White
Write-Host "   cd backend"
Write-Host "   git init"
Write-Host '   git remote add azure https://hallux-fefsdqc6fmbmdkcu.scm.eastasia-01.azurewebsites.net/Hallux.git'
Write-Host "   git add ."
Write-Host '   git commit -m "Deploy backend"'
Write-Host "   git push azure main"
Write-Host ""

Write-Host "5️⃣  Test Deployment" -ForegroundColor Cyan
Write-Host "   curl $BACKEND_URL/api/health"
Write-Host ""

Write-Host "=================================="  -ForegroundColor Cyan
Write-Host "🎯 Quick Commands to Run Now:" -ForegroundColor Yellow
Write-Host "=================================="  -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az --version 2>$null
    Write-Host "✅ Azure CLI installed" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Run these commands to deploy:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "cd backend" -ForegroundColor White
    Write-Host "Compress-Archive -Path * -DestinationPath deploy.zip -Force" -ForegroundColor White
    Write-Host "az webapp deployment source config-zip --resource-group mcve --name Hallux --src deploy.zip" -ForegroundColor White
    
} catch {
    Write-Host "⚠️  Azure CLI not found" -ForegroundColor Red
    Write-Host "Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=================================="  -ForegroundColor Cyan
