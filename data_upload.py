
import json
from os import getenv

from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "clinicalData"
COLLECTION_NAME = "patients"
JSON_FILE_PATH = "model_evaluation_data.json"


print("Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
print("Connection successful.")

try:

    print(f"Clearing existing documents in '{COLLECTION_NAME}' collection...")
    collection.delete_many({})
    print("Collection cleared.")


    print(f"Loading data from '{JSON_FILE_PATH}'...")
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)
    print(f"Loaded {len(data)} documents.")


    print("Inserting documents into MongoDB...")
    collection.insert_many(data)
    print("✅ Data upload successful!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    client.close()
    print("MongoDB connection closed.")