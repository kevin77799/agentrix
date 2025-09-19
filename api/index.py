# Vercel Serverless Function for AgentriX API
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import Optional
import os
import random
import datetime
from bson import ObjectId
import pymongo
from pymongo import MongoClient

# --- Database Connection ---
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

def get_database():
    """Get database connection with error handling"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client['agentrix_db']
        return db['advisories']
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# --- Agricultural Logic Functions ---
def get_weather_data(lat: float, lon: float):
    """Simulate weather data"""
    weather_conditions = ["Sunny", "Partly Cloudy", "Rainy", "Overcast", "Thunderstorms"]
    return {
        "temperature_celsius": random.randint(20, 35),
        "description": random.choice(weather_conditions),
        "humidity": random.randint(40, 80),
        "location": f"Lat: {lat}, Lon: {lon}"
    }

def get_crop_recommendation(soil_type: str):
    """Get crop recommendation based on soil type"""
    soil_type = soil_type.lower()
    if "clay" in soil_type or "alluvial" in soil_type:
        return "Rice"
    elif "sandy" in soil_type:
        return "Groundnut"
    elif "black" in soil_type:
        return "Cotton"
    elif "red" in soil_type:
        return "Millets"
    elif "loam" in soil_type:
        return "Wheat"
    else:
        return "Rice"

def get_market_price(crop: str):
    """Get simulated market price"""
    base_prices = {
        "Rice": 2500, "Wheat": 2200, "Cotton": 6000,
        "Groundnut": 5500, "Millets": 3200, "Corn": 2800
    }
    base_price = base_prices.get(crop, 2500)
    return base_price + random.randint(-200, 300)

def get_resource_advice(crop: str):
    """Get resource management advice"""
    resource_map = {
        "Rice": {
            "fertilizer": "NPK 20:10:10, apply 100kg per acre during planting",
            "irrigation": "Maintain 2-3 cm water level throughout growing season",
            "fertilizer_ml": "ഏക്കറിന് 100 കിലോ NPK 20:10:10 വളം നടീൽ സമയത്ത് പ്രയോഗിക്കുക",
            "irrigation_ml": "വളർച്ചാ കാലത്തിലുടനീളം 2-3 സെന്റിമീറ്റർ ജല നിരപ്പ് നിലനിർത്തുക"
        },
        "Wheat": {
            "fertilizer": "Urea 120kg + DAP 100kg per acre",
            "irrigation": "3-4 irrigations during growing season",
            "fertilizer_ml": "ഏക്കറിന് യൂറിയ 120kg + DAP 100kg",
            "irrigation_ml": "വളർച്ചാ കാലത്ത് 3-4 ജലസേചനം"
        },
        "Cotton": {
            "fertilizer": "NPK 17:17:17, 150kg per acre with micronutrients",
            "irrigation": "Weekly irrigation, avoid waterlogging",
            "fertilizer_ml": "ഏക്കറിന് NPK 17:17:17, 150kg മൈക്രോ ന്യൂട്രിയന്റുകൾ സഹിതം",
            "irrigation_ml": "ആഴ്ചതോറും ജലസേചനം, വെള്ളം കെട്ടുന്നത് ഒഴിവാക്കുക"
        }
    }
    return resource_map.get(crop, resource_map["Rice"])

def analyze_disease(image_bytes: bytes):
    """Simulate disease analysis"""
    if not image_bytes:
        return {"disease": "No image provided", "confidence": 0.0}
    
    diseases = ["Healthy", "Bacterial Blight", "Brown Spot", "Leaf Smut", "Fungal Infection"]
    return {
        "disease": random.choice(diseases),
        "confidence": random.uniform(0.7, 0.95)
    }

def generate_advice(weather, crop, price, resources, disease, lang="en"):
    """Generate final advice in requested language"""
    if lang == "ml":
        advice = f"🌤️ **കാലാവസ്ഥ:** {weather['temperature_celsius']}°C, {weather['description']}\n\n"
        advice += f"🌾 **വിള ശുപാർശ:** {crop} നടാൻ ശുപാർശ ചെയ്യുന്നു\n\n"
        advice += f"💰 **വിപണി വില:** ₹{price} ക്വിന്റലിന്\n\n"
        if resources:
            advice += f"🌱 **വിഭവ ഉപദേശം:**\n• വളം: {resources['fertilizer_ml']}\n• ജലസേചനം: {resources['irrigation_ml']}\n\n"
        if disease and disease['disease'] != "No image provided":
            advice += f"🔬 **രോഗ വിശകലനം:** {disease['disease']} ({disease['confidence']*100:.1f}% കൃത്യത)\n"
    else:
        advice = f"🌤️ **Weather:** {weather['temperature_celsius']}°C, {weather['description']}\n\n"
        advice += f"🌾 **Crop Recommendation:** {crop} is recommended for your soil\n\n"
        advice += f"💰 **Market Price:** ₹{price} per quintal\n\n"
        if resources:
            advice += f"🌱 **Resource Advice:**\n• Fertilizer: {resources['fertilizer']}\n• Irrigation: {resources['irrigation']}\n\n"
        if disease and disease['disease'] != "No image provided":
            advice += f"🔬 **Disease Analysis:** {disease['disease']} ({disease['confidence']*100:.1f}% confidence)\n"
    
    return advice

# --- FastAPI App ---
app = FastAPI(title="AgentriX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AgentriX Agricultural Advisory API", "status": "healthy"}

@app.post("/get-advice")
async def get_advice(
    gps: str = Form(...),
    soil_type: str = Form(...),
    lang: str = Form("en"),
    leaf_photo: Optional[UploadFile] = File(None)
):
    try:
        # Parse GPS
        try:
            lat, lon = map(float, gps.split(','))
        except:
            lat, lon = 10.0, 76.0  # Default to Kerala coordinates
        
        # Get weather data
        weather = get_weather_data(lat, lon)
        
        # Get crop recommendation
        crop = get_crop_recommendation(soil_type)
        
        # Get market price
        price = get_market_price(crop)
        
        # Get resource advice
        resources = get_resource_advice(crop)
        
        # Analyze disease (if image provided)
        disease = None
        if leaf_photo:
            image_data = await leaf_photo.read()
            disease = analyze_disease(image_data)
        
        # Generate final advice
        advice = generate_advice(weather, crop, price, resources, disease, lang)
        
        # Try to save to database
        advisory_collection = get_database()
        request_id = "no-db"
        if advisory_collection:
            try:
                result = advisory_collection.insert_one({
                    "gps": gps,
                    "soil_type": soil_type,
                    "lang": lang,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc),
                    "results": {
                        "weather": weather,
                        "crop": crop,
                        "price": price,
                        "disease": disease
                    }
                })
                request_id = str(result.inserted_id)
            except Exception as e:
                print(f"Database save error: {e}")
        
        return {
            "success": True,
            "request_id": request_id,
            "advice": {"en": advice, "ml": advice},
            "data": {
                "weather": weather,
                "crop": crop,
                "price": price,
                "disease": disease
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel handler
handler = Mangum(app)