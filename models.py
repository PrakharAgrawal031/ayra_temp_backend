from pydantic import BaseModel
from typing import List

# --- Pydantic Models ---

class GraphRequest(BaseModel):
    prompt: str

class GraphDataPoint(BaseModel):
    date: str
    value: float

class GraphResponse(BaseModel):
    xAxisLabel: str
    yAxisLabel: str
    data: List[GraphDataPoint]