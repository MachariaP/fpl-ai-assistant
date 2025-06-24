import pymongo
import certifi
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    print("MONGODB_URI not set")
    exit(1)

try:
    client = pymongo.MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=30000,
        tls=True,
        tlsCAFile=certifi.where()
    )
    client.admin.command('ping')
    print("MongoDB Atlas connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
