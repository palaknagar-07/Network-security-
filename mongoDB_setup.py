import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI
uri = os.getenv("MONGODB_URI")

# Create MongoDB client
client = MongoClient(uri)

# Test connection
try:
    client.admin.command("ping")
    print("✅ Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    print("❌ Connection failed:", e)