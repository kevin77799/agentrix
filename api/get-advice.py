# Main API endpoint for Vercel
from http.server import BaseHTTPRequestHandler
import json
import os
import random
import datetime
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            # Get request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse form data (simplified)
            data = parse_qs(post_data)
            gps = data.get('gps', ['10.0,76.0'])[0]
            soil_type = data.get('soil_type', ['clay'])[0]
            lang = data.get('lang', ['en'])[0]

            # Process the request
            result = self.process_agricultural_request(gps, soil_type, lang)
            
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": str(e), "success": False}
            self.wfile.write(json.dumps(error_response).encode())

    def process_agricultural_request(self, gps, soil_type, lang):
        """Process agricultural advisory request"""
        
        # Parse GPS
        try:
            lat, lon = map(float, gps.split(','))
        except:
            lat, lon = 10.0, 76.0

        # Weather simulation
        weather_conditions = ["Sunny", "Partly Cloudy", "Rainy", "Overcast"]
        weather = {
            "temperature_celsius": random.randint(20, 35),
            "description": random.choice(weather_conditions),
            "humidity": random.randint(40, 80)
        }

        # Crop recommendation
        soil_type_lower = soil_type.lower()
        if "clay" in soil_type_lower or "alluvial" in soil_type_lower:
            crop = "Rice"
        elif "sandy" in soil_type_lower:
            crop = "Groundnut"
        elif "black" in soil_type_lower:
            crop = "Cotton"
        else:
            crop = "Rice"

        # Market price simulation
        base_prices = {"Rice": 2500, "Wheat": 2200, "Cotton": 6000, "Groundnut": 5500}
        price = base_prices.get(crop, 2500) + random.randint(-200, 300)

        # Generate advice
        if lang == "ml":
            advice = f"🌤️ കാലാവസ്ഥ: {weather['temperature_celsius']}°C, {weather['description']}\n\n"
            advice += f"🌾 വിള ശുപാർശ: {crop} നടാൻ ശുപാർശ ചെയ്യുന്നു\n\n"
            advice += f"💰 വിപണി വില: ₹{price} ക്വിന്റലിന്"
        else:
            advice = f"🌤️ Weather: {weather['temperature_celsius']}°C, {weather['description']}\n\n"
            advice += f"🌾 Crop Recommendation: {crop} is recommended for your {soil_type} soil\n\n"
            advice += f"💰 Market Price: ₹{price} per quintal"

        return {
            "success": True,
            "advice": {"en": advice, "ml": advice},
            "data": {
                "weather": weather,
                "crop": crop,
                "price": price,
                "location": f"Lat: {lat}, Lon: {lon}"
            },
            "timestamp": datetime.datetime.now().isoformat()
        }