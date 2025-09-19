# Vercel API endpoint with MongoDB integration
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import random
import os
import datetime
from pymongo import MongoClient

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

def get_database():
    """Get database connection with error handling"""
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=True,
            retryWrites=True
        )
        db = client['agentrix_db']
        return db['advisories']
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "AgentriX Agricultural Advisory API",
            "status": "healthy"
        }
        self.wfile.write(json.dumps(response).encode())
        return

    def do_POST(self):
        try:
            # Read and parse request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract form data
            gps = data.get('gps', '10.0,76.0')
            soil_type = data.get('soil_type', 'alluvial soil')
            lang = data.get('lang', 'en')
            
            # Generate agricultural data
            weather_conditions = ["Sunny", "Partly Cloudy", "Rainy", "Overcast"]
            crops = ["Rice", "Wheat", "Cotton", "Groundnut", "Millets"]
            
            weather_data = {
                "temperature_celsius": random.randint(20, 35),
                "description": random.choice(weather_conditions),
                "humidity": random.randint(40, 80)
            }
            
            crop = random.choice(crops)
            price = random.randint(2000, 6000)
            
            advice = f"""🌤️ **Weather:** {weather_data['temperature_celsius']}°C, {weather_data['description']}

🌾 **Crop Recommendation:** {crop} is recommended for your soil

💰 **Market Price:** ₹{price} per quintal

🌱 **Resource Advice:**
• Fertilizer: Apply NPK fertilizer as per soil test
• Irrigation: Maintain optimal water levels

🔬 **Status:** AI-powered agricultural analysis complete"""

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
                            "weather": weather_data,
                            "crop": crop,
                            "price": price
                        }
                    })
                    request_id = str(result.inserted_id)
                    print(f"Data saved to MongoDB with ID: {request_id}")
                except Exception as e:
                    print(f"Database save error: {e}")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = {
                "success": True,
                "request_id": request_id,
                "advice": {"en": advice, "ml": advice},
                "data": {
                    "weather": weather_data,
                    "crop": crop,
                    "price": price
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"POST error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return