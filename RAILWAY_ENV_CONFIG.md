# Environment Variables for Railway Deployment

## Required Environment Variables

### Database Configuration
- `MONGODB_URI` - MongoDB connection string (use MongoDB Atlas or Railway MongoDB addon)

### Microservice URLs (for production)
- `WEATHER_SERVICE_URL` - URL of deployed weather agent service
- `CROP_SERVICE_URL` - URL of deployed crop agent service  
- `MARKET_SERVICE_URL` - URL of deployed market agent service
- `RESOURCE_SERVICE_URL` - URL of deployed resource agent service
- `DISEASE_SERVICE_URL` - URL of deployed disease agent service

### Example Values for Railway
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/agentrix_db
WEATHER_SERVICE_URL=https://weather-agent-production.up.railway.app
CROP_SERVICE_URL=https://crop-agent-production.up.railway.app
MARKET_SERVICE_URL=https://market-agent-production.up.railway.app
RESOURCE_SERVICE_URL=https://resource-agent-production.up.railway.app
DISEASE_SERVICE_URL=https://disease-agent-production.up.railway.app
```

## Railway Services Setup

You'll need to create 7 separate Railway services:

1. **Main Backend** (backend/) - Orchestrates all agents
2. **Dashboard** (dashboard.py) - Streamlit admin dashboard
3. **Frontend** (frontend/) - React UI
4. **Disease Agent** (backend/disease_agent/) - Plant disease detection
5. **Crop Agent** (backend/crop_agent/) - Crop recommendations
6. **Market Agent** (backend/market_agent/) - Market price predictions  
7. **Weather Agent** (backend/weather_agent/) - Weather forecasting
8. **Resource Agent** (backend/resource_agent/) - Resource management advice