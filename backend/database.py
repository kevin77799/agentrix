# In backend/database.py

from pymongo import MongoClient
import os

# Get MongoDB connection string from environment variable or use localhost as fallback
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

# Establish a connection to the MongoDB server
client = MongoClient(MONGODB_URI)

# Select your database (it will be created if it doesn't exist)
db = client['agentrix_db']

# Get a reference to your collections (like tables in SQL)
farmer_collection = db['farmers']
advisory_collection = db['advisories']

print(f"MongoDB connection established successfully to: {MONGODB_URI}")