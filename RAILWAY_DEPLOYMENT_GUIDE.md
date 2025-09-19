# AgentriX Railway Deployment Guide

## Overview
This guide will help you deploy your AgentriX application to Railway. The application consists of multiple microservices that need to be deployed separately.

## Architecture
Your AgentriX application has:
- **Main Backend**: FastAPI orchestrator that coordinates all agents
- **Streamlit Dashboard**: Admin dashboard for monitoring
- **React Frontend**: User interface
- **5 Microservices**: Disease, Crop, Market, Weather, and Resource agents
- **MongoDB Database**: For storing farmer data and advisories

## Prerequisites

1. **GitHub Account**: Railway deploys from GitHub repositories
2. **Railway Account**: Sign up at https://railway.app
3. **MongoDB Atlas Account**: For hosted MongoDB (recommended)

## Step-by-Step Deployment

### 1. Prepare Your Repository

First, push your code to GitHub:

```bash
# Initialize git repository if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare AgentriX for Railway deployment"

# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/yourusername/agentrix.git

# Push to GitHub
git push -u origin main
```

### 2. Set Up MongoDB Database

**Option A: MongoDB Atlas (Recommended)**
1. Go to https://www.mongodb.com/atlas
2. Create a free cluster
3. Create a database user
4. Get your connection string (it will look like: `mongodb+srv://username:password@cluster.mongodb.net/agentrix_db`)

**Option B: Railway MongoDB Plugin**
1. In Railway dashboard, add MongoDB plugin to any service
2. Copy the connection string from the plugin

### 3. Deploy Services to Railway

You need to create **8 separate Railway projects**:

#### A. Main Backend Service
1. Create new project in Railway
2. Connect your GitHub repository
3. Set root directory to: `backend`
4. Add environment variables:
   ```
   MONGODB_URI=your_mongodb_connection_string
   WEATHER_SERVICE_URL=https://weather-agent-production.up.railway.app
   CROP_SERVICE_URL=https://crop-agent-production.up.railway.app
   MARKET_SERVICE_URL=https://market-agent-production.up.railway.app
   RESOURCE_SERVICE_URL=https://resource-agent-production.up.railway.app
   DISEASE_SERVICE_URL=https://disease-agent-production.up.railway.app
   ```

#### B. Streamlit Dashboard
1. Create new project in Railway
2. Connect your GitHub repository  
3. Set root directory to: `/` (root folder)
4. Set custom build command: `pip install -r dashboard_requirements.txt`
5. Set custom start command: `streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0`
6. Add environment variables:
   ```
   MONGODB_URI=your_mongodb_connection_string
   ```

#### C. React Frontend
1. Create new project in Railway
2. Connect your GitHub repository
3. Set root directory to: `frontend`
4. Railway will auto-detect React and build it
5. Add environment variables if your React app needs to connect to backend:
   ```
   REACT_APP_BACKEND_URL=https://your-main-backend.up.railway.app
   ```

#### D. Disease Agent Microservice
1. Create new project in Railway
2. Connect your GitHub repository
3. Set root directory to: `backend/disease_agent`
4. Railway will use the Procfile automatically

#### E. Crop Agent Microservice  
1. Create new project in Railway
2. Connect your GitHub repository
3. Set root directory to: `backend/crop_agent`

#### F. Market Agent Microservice
1. Create new project in Railway
2. Connect your GitHub repository
3. Set root directory to: `backend/market_agent`

#### G. Weather Agent Microservice
1. Create new project in Railway
2. Connect your GitHub repository
3. Set root directory to: `backend/weather_agent`

#### H. Resource Agent Microservice
1. Create new project in Railway
2. Connect your GitHub repository
3. Set root directory to: `backend/resource_agent`

### 4. Update Environment Variables

After all services are deployed, you'll get URLs for each service. Update the main backend's environment variables with the actual URLs:

```
WEATHER_SERVICE_URL=https://your-weather-agent.up.railway.app
CROP_SERVICE_URL=https://your-crop-agent.up.railway.app
MARKET_SERVICE_URL=https://your-market-agent.up.railway.app
RESOURCE_SERVICE_URL=https://your-resource-agent.up.railway.app
DISEASE_SERVICE_URL=https://your-disease-agent.up.railway.app
```

### 5. Test Your Deployment

1. Visit your frontend URL to test the user interface
2. Visit your dashboard URL to check the admin panel
3. Test API endpoints on your main backend
4. Check Railway logs for any errors

## Important Notes

- **Disease Agent**: Contains a PyTorch model file (`plant_disease_model_1_latest.pt`). Ensure this file is committed to your repository.
- **CORS**: Make sure your backend allows requests from your frontend domain.
- **File Uploads**: Disease detection requires file upload capability - ensure this works in production.
- **Database**: All services that need database access should use the same MONGODB_URI.

## Troubleshooting

**Common Issues:**
1. **Build Failures**: Check the build logs in Railway dashboard
2. **Connection Errors**: Verify environment variables are set correctly
3. **CORS Issues**: Update CORS settings in your FastAPI apps
4. **File Size Limits**: Railway has file size limits for deployments

**Debugging:**
- Use Railway logs to debug issues
- Test each microservice individually
- Verify environment variables are correctly set

## Cost Optimization

- Railway offers $5 free credit monthly
- Each service counts toward your usage
- Consider combining some microservices if needed
- Use Railway's sleep feature for non-production services

Your AgentriX application is now ready for production deployment on Railway!