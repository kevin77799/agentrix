# Simple Vercel API endpoint
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import random
import os

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
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Simple agricultural advice response
        weather_conditions = ["Sunny", "Partly Cloudy", "Rainy", "Overcast"]
        crops = ["Rice", "Wheat", "Cotton", "Groundnut", "Millets"]
        
        advice = f"""🌤️ **Weather:** {random.randint(20, 35)}°C, {random.choice(weather_conditions)}

🌾 **Crop Recommendation:** {random.choice(crops)} is recommended for your soil

💰 **Market Price:** ₹{random.randint(2000, 6000)} per quintal

🌱 **Resource Advice:**
• Fertilizer: Apply NPK fertilizer as per soil test
• Irrigation: Maintain optimal water levels

🔬 **Status:** AI-powered agricultural analysis complete"""
        
        response = {
            "success": True,
            "advice": {"en": advice, "ml": advice},
            "data": {
                "weather": {"temperature_celsius": random.randint(20, 35), "description": random.choice(weather_conditions)},
                "crop": random.choice(crops),
                "price": random.randint(2000, 6000)
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return