# Hallux Backend Quick Start Guide

## 🚀 Quick Setup (Windows)

### Step 1: Create Virtual Environment
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment
```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env and add your API keys
notepad .env
```

### Step 4: Run the Server
```powershell
python -m app.main
```

Or using uvicorn directly:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Test the API
Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Root**: http://localhost:8000/

## 📝 Quick API Test

### Test Citation Verification
```powershell
# Using PowerShell
$body = @{
    citation = "Smith et al. (2023). Deep Learning for Citation Verification. arXiv:2301.12345"
    context = "Recent studies have shown..."
    options = @{
        enable_ai_scoring = $true
        check_content = $true
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/verify-citation" -Method Post -Body $body -ContentType "application/json"
```

### Test Text Verification
```powershell
$body = @{
    text = "According to Smith et al. (2023), AI models can hallucinate citations."
    format = "plain"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/verify-text" -Method Post -Body $body -ContentType "application/json"
```

## 🔧 Troubleshooting

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Import Errors
```powershell
# Make sure you're in the backend directory
cd backend

# Run with Python module syntax
python -m app.main
```

### Missing Dependencies
```powershell
pip install -r requirements.txt --force-reinstall
```

## 📚 Next Steps

1. **Add API Keys** to `.env` for full functionality:
   - `OPENAI_API_KEY` - For AI reasoning
   - `GEMINI_API_KEY` - Alternative AI model
   - `SERPER_API_KEY` - For web search

2. **Install PostgreSQL** (optional, for persistence):
   ```powershell
   # Update DATABASE_URL in .env
   ```

3. **Install Redis** (optional, for caching):
   ```powershell
   # Update REDIS_URL in .env
   ```

4. **Explore API Documentation**:
   Visit http://localhost:8000/docs to see all available endpoints

## 🎯 For Hackathon Demo

The backend works without database/Redis for quick testing!
Just make sure to add at least one AI API key (OpenAI or Gemini) in `.env`.

All verification layers will work in "demo mode" showing the verification process even without external APIs configured.
