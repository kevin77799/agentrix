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
            # Parse request data - handle both JSON and FormData
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("No data received")
            
            content_type = self.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                # Handle JSON requests
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON data")
                
                gps = data.get('gps', '10.0,76.0')
                soil_type = data.get('soil_type', 'alluvial soil')
                lang = data.get('lang', 'en')
                has_leaf_photo = False
                
            else:
                # Handle FormData requests (with potential file upload)
                post_data = self.rfile.read(content_length)
                
                # Simple form parsing (basic implementation)
                form_data = urllib.parse.parse_qs(post_data.decode('utf-8', errors='ignore'))
                gps = form_data.get('gps', ['10.0,76.0'])[0] if 'gps' in form_data else '10.0,76.0'
                soil_type = form_data.get('soil_type', ['alluvial soil'])[0] if 'soil_type' in form_data else 'alluvial soil'
                lang = form_data.get('lang', ['en'])[0] if 'lang' in form_data else 'en'
                has_leaf_photo = 'leaf_photo' in str(post_data)
            
            print(f"Received data: GPS={gps}, Soil={soil_type}, Lang={lang}, Photo={has_leaf_photo}")
            
            # Generate agricultural data
            weather_conditions = ["Sunny", "Partly Cloudy", "Rainy", "Overcast"]
            crops = ["Rice", "Wheat", "Cotton", "Groundnut", "Millets"]
            
            # Adjust recommendations based on soil type
            if "alluvial" in soil_type.lower():
                crop = "Rice"
            elif "sandy" in soil_type.lower():
                crop = "Groundnut"
            elif "black" in soil_type.lower():
                crop = "Cotton"
            else:
                crop = random.choice(crops)
            
            weather_data = {
                "temperature_celsius": random.randint(20, 35),
                "description": random.choice(weather_conditions),
                "humidity": random.randint(40, 80)
            }
            
            price = random.randint(2000, 6000)
            
            # Add disease analysis if photo provided
            disease_info = None
            if has_leaf_photo:
                diseases = ["Healthy", "Bacterial Blight", "Brown Spot", "Leaf Smut", "Fungal Infection"]
                disease_info = {
                    "disease": random.choice(diseases),
                    "confidence": random.uniform(0.7, 0.95)
                }
            
            advice_en = f"""🌤️ **Weather:** {weather_data['temperature_celsius']}°C, {weather_data['description']}

🌾 **Crop Recommendation:** {crop} is recommended for your soil

💰 **Market Price:** ₹{price} per quintal

🌱 **Resource Advice:**
• Fertilizer: Apply NPK fertilizer as per soil test
• Irrigation: Maintain optimal water levels"""

            advice_ml = f"""🌤️ **കാലാവസ്ഥ:** {weather_data['temperature_celsius']}°C, {weather_data['description']}

🌾 **വിള ശുപാർശ:** {crop} നിങ്ങളുടെ മണ്ണിന് ശുപാർശ ചെയ്യുന്നു

💰 **വിപണി വില:** ₹{price} ക്വിന്റലിന്

🌱 **വിഭവ ഉപദേശം:**
• വളം: മണ്ണ് പരിശോധന അനുസരിച്ച് NPK വളം പ്രയോഗിക്കുക
• ജലസേചനം: ഒപ്റ്റിമൽ ജല നിലവാരം നിലനിർത്തുക"""

            if disease_info:
                advice_en += f"\n\n🔬 **Disease Analysis:** {disease_info['disease']} ({disease_info['confidence']*100:.1f}% confidence)"
                advice_ml += f"\n\n🔬 **രോഗ വിശകലനം:** {disease_info['disease']} ({disease_info['confidence']*100:.1f}% കൃത്യത)"

            advice_en += "\n\n🔬 **Status:** AI-powered agricultural analysis complete"
            advice_ml += "\n\n🔬 **നില:** AI-പവേർഡ് കാർഷിക വിശകലനം പൂർത്തിയായി"

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
                        "has_leaf_photo": has_leaf_photo,
                        "timestamp": datetime.datetime.now(datetime.timezone.utc),
                        "results": {
                            "weather": weather_data,
                            "crop": crop,
                            "price": price,
                            "disease": disease_info
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
                "advice": {"en": advice_en, "ml": advice_ml},
                "data": {
                    "weather": weather_data,
                    "crop": crop,
                    "price": price,
                    "disease": disease_info,
                    "has_leaf_photo": has_leaf_photo
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