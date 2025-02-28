from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Async MongoDB Client
client = AsyncIOMotorClient(MONGO_URI)
db = client.learnscribe


def get_database():
    """Returns the MongoDB database instance."""
    return db


def close_mongo_connection():
    """Closes the MongoDB connection."""
    client.close()
