# main.py
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import certifi
from gemini import evaluate_patient_record, generate_graph_data
from fastapi.middleware.cors import CORSMiddleware
from models import GraphRequest, GraphResponse

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "clinicalData"
COLLECTION_NAME = "patients"




app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Ensure the MongoDB connection uses the certifi CA file for compatibility
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

@app.get("/")
def read_root():
    return {"message": "Patient Data API is running. Go to /docs for API documentation."}


@app.get("/api/v1/patients", response_model=List[Dict[str, Any]])
async def get_all_patients():
    """
    Retrieves a list of all patients with their ID, name, archetype, and demographics.
    """
    patients = list(collection.find({}, {
        "_id": 0,  # Exclude the default MongoDB _id
        "patient_id": 1,
        "patient_name": 1, # Added patient_name
        "archetype": 1,
        "demographics": 1
    }))
    return patients


@app.get("/api/v1/patients/{patient_id}", response_model=Dict[str, Any])
async def get_patient_details(patient_id: str):
    """
    Retrieves a comprehensive set of details for a single patient,
    including demographics, allergies, clinical timeline, and AI-generated summaries.
    """
    # Updated projection to include all the new fields
    projection = {
        "_id": 0,
        "patient_id": 1,
        "patient_name": 1,
        "demographics": 1,
        "allergies": 1,
        "clinical_timeline": 1,
        "biomistral_summary": 1,
        "correlations": 1
    }
    
    patient = collection.find_one({"patient_id": patient_id}, projection)
    
    if patient:
        return patient
    raise HTTPException(status_code=404, detail=f"Patient with ID '{patient_id}' not found.")


@app.get("/api/v1/patients/report/{patient_id}", response_model=Dict[str, Any])
async def get_patient_reports(patient_id: str):
    """
    Retrieves a comprehensive set of details for a single patient,
    including demographics, allergies, clinical timeline, and AI-generated summaries.
    """
    # Updated projection to include all the new fields
    projection = {
        "_id": 0,
        "patient_id": 1,
        "patient_name": 1,
        "demographics": 1,
        "allergies": 1,
        "clinical_timeline": 1,
        "biomistral_summary": 1,
        "correlations": 1
    }

    patient = collection.find_one({"patient_id": patient_id}, projection)

    if patient:
        return evaluate_patient_record(patient)
    raise HTTPException(status_code=404, detail=f"Patient with ID '{patient_id}' not found.")


@app.post("/api/v1/patients/graph/{patient_id}", response_model=GraphResponse)
async def get_graph_data_for_patient(patient_id: str, request: GraphRequest):
    """
    Generates time-series data for a specific metric from a patient's clinical timeline
    based on a natural language prompt. Returns data along with axis labels.
    """
    projection = {
        "_id": 0,
        "patient_id": 1,
        "clinical_timeline": 1
    }

    patient = collection.find_one({"patient_id": patient_id}, projection)

    if not patient or "clinical_timeline" not in patient:
        raise HTTPException(status_code=404, detail=f"Clinical timeline for patient with ID '{patient_id}' not found.")

    graph_data = generate_graph_data(patient["clinical_timeline"], request.prompt)

    if "error" in graph_data:
        raise HTTPException(status_code=500, detail=f"Failed to generate graph data: {graph_data['error']}")

    return graph_data