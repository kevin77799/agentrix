@echo off
echo Preparing AgentriX for Railway Deployment...
echo.

echo Step 1: Initialize Git Repository
git init
echo.

echo Step 2: Add all files to git
git add .
echo.

echo Step 3: Create initial commit
git commit -m "Prepare AgentriX for Railway deployment - Add all deployment configurations"
echo.

echo Step 4: Instructions for GitHub setup
echo.
echo NEXT STEPS:
echo 1. Create a new repository on GitHub.com
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_GITHUB_URL
echo 4. Run: git push -u origin main
echo 5. Follow the RAILWAY_DEPLOYMENT_GUIDE.md for Railway setup
echo.

echo Deployment files created successfully!
echo - Backend configured with environment variables
echo - Frontend ready with serve configuration  
echo - All microservices have Procfiles and requirements.txt
echo - Dashboard configured for Streamlit deployment
echo - MongoDB connection updated for production
echo.

pause