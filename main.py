# main.py
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import List, Dict, Any


MONGO_URI = "mongodb+srv://ayratempbackend:IM0NenVra30NIzX9@prakhar.eywoyo2.mongodb.net/?retryWrites=true&w=majority&appName=Prakhar"
DB_NAME = "clinicalData"
COLLECTION_NAME = "patients"


app = FastAPI()
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]



@app.get("/")
def read_root():
    return {"message": "Patient Data API is running. Go to /docs for API documentation."}


@app.get("/api/v1/patients", response_model=List[Dict[str, Any]])
async def get_all_patients():
    """
    Retrieves a list of all patients with their ID, archetype, and demographics.
    """
    patients = list(collection.find({}, {
        "_id": 0,  # Exclude the default MongoDB _id
        "patient_id": 1,
        "archetype": 1,
        "demographics": 1
    }))
    return patients


@app.get("/api/v1/patients/{patient_id}", response_model=Dict[str, Any])
async def get_patient_details(patient_id: str):
    """
    Retrieves specific demographic and clinical details for a single patient.
    """
    patient = collection.find_one(
        {"patient_id": patient_id},
        {
            "_id": 0, # Exclude the default MongoDB _id
            "patient_id": 1,
            "demographics": 1,
            "clinical_timeline": 1
        }
    )
    if patient:
        return patient
    raise HTTPException(status_code=404, detail=f"Patient with ID '{patient_id}' not found.")