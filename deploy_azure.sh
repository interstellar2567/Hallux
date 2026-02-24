#!/bin/bash

# 🚀 Azure Backend Deployment Script for Hallux

echo "=================================="
echo "Azure Backend Deployment"
echo "=================================="

# Configuration
RESOURCE_GROUP="mcve"
APP_NAME="Hallux"
LOCATION="eastasia"

echo ""
echo "✅ Your backend is already created!"
echo "URL: https://hallux-fefsdqc6fmbmdkcu.eastasia-01.azurewebsites.net"
echo ""

# Step 1: Configure Environment Variables
echo "📝 Step 1: Setting environment variables..."
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    OPENAI_API_KEY="${OPENAI_API_KEY:-your-key-here}" \
    GOOGLE_API_KEY="${GOOGLE_API_KEY:-your-key-here}" \
    ENV="production" \
    LOG_LEVEL="INFO" \
    DEBUG="False" \
    ALLOWED_ORIGINS="*"

echo "✅ Environment variables set"

# Step 2: Configure Startup Command
echo ""
echo "📝 Step 2: Configuring startup command..."
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120"

echo "✅ Startup command configured"

# Step 3: Deploy Code
echo ""
echo "📝 Step 3: Deploying code from local Git..."
echo "First, let's check if deployment source is configured..."

# Get deployment URL
DEPLOYMENT_URL=$(az webapp deployment source config-local-git \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query url \
  --output tsv 2>/dev/null)

if [ -z "$DEPLOYMENT_URL" ]; then
  echo "⚠️ Deployment source not configured. Setting up..."
  az webapp deployment source config-local-git \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP
else
  echo "✅ Deployment source already configured"
fi

# Get deployment credentials
echo ""
echo "📝 Getting deployment credentials..."
DEPLOYMENT_USER=$(az webapp deployment list-publishing-credentials \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query publishingUserName \
  --output tsv)

echo "✅ Deployment user: $DEPLOYMENT_USER"

echo ""
echo "=================================="
echo "✅ Configuration Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Add Azure remote (run from project root):"
echo "   cd backend"
echo "   git init (if not already initialized)"
echo "   git remote add azure https://$DEPLOYMENT_USER@hallux-fefsdqc6fmbmdkcu.scm.eastasia-01.azurewebsites.net/Hallux.git"
echo ""
echo "2. Deploy your code:"
echo "   git add ."
echo "   git commit -m 'Deploy to Azure'"
echo "   git push azure main"
echo ""
echo "3. Test deployment:"
echo "   curl https://hallux-fefsdqc6fmbmdkcu.eastasia-01.azurewebsites.net/api/health"
echo ""
echo "=================================="
