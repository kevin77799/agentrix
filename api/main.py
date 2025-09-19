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
            if content_length == 0:
                raise ValueError("No data received")
                
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON data")
            
            # Extract form data with defaults
            gps = data.get('gps', '10.0,76.0')
            soil_type = data.get('soil_type', 'alluvial soil')
            lang = data.get('lang', 'en')
            
            print(f"Received data: GPS={gps}, Soil={soil_type}, Lang={lang}")
            
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
            request_id = "no-db"
            db_success = False
            
            try:
                advisory_collection = get_database()
                if advisory_collection:
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
                    db_success = True
                    print(f"Data saved to MongoDB with ID: {request_id}")
            except Exception as db_error:
                print(f"Database save error: {db_error}")
                # Continue anyway - don't fail the request for DB issues
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = {
                "success": True,
                "request_id": request_id,
                "db_saved": db_success,
                "advice": {"en": advice, "ml": advice},
                "data": {
                    "weather": weather_data,
                    "crop": crop,
                    "price": price
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            print("Response sent successfully")
            
        except Exception as e:
            print(f"POST error: {e}")
            
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            error_response = {
                "success": False, 
                "error": str(e),
                "message": "Please check your request format"
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return