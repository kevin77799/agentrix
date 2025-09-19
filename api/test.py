# Simple test API endpoint
from http.server import BaseHTTPRequestHandler
import json
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "AgentriX Agricultural Advisory API - Test Version",
            "status": "healthy"
        }
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        try:
            # Send success headers first
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Simple response without complex processing
            advice = """🌤️ **Weather:** 28°C, Sunny

🌾 **Crop Recommendation:** Rice is recommended for your soil

💰 **Market Price:** ₹2800 per quintal

🌱 **Resource Advice:**
• Fertilizer: Apply NPK fertilizer as per soil test
• Irrigation: Maintain optimal water levels

🔬 **Status:** Test agricultural analysis complete"""

            response = {
                "success": True,
                "request_id": "test-123",
                "advice": {"en": advice, "ml": advice},
                "data": {
                    "weather": {"temperature_celsius": 28, "description": "Sunny"},
                    "crop": "Rice",
                    "price": 2800
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # If anything fails, send a simple error
            error_response = {
                "success": False,
                "error": f"Test API Error: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return