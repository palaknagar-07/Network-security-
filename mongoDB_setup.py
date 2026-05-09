import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI
url = os.getenv("MONGODB_URL")
print(f"MongoDB URL: {url}")

# Create MongoDB client
client = MongoClient(url)

# Test connection
try:
    client.admin.command("ping")
    print("✅ Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    print("❌ Connection failed:", e)