# Simple health check endpoint
from http.server import BaseHTTPRequestHandler
import json
import os
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "AgentriX API is running on Vercel!",
            "status": "healthy",
            "version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return