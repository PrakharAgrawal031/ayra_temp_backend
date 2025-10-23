from pydantic import BaseModel
from typing import List, Union

# --- Pydantic Models ---

class GraphRequest(BaseModel):
    prompt: str

class GraphDataPoint(BaseModel):
    x: Union[str, float, int]
    y: float

class GraphResponse(BaseModel):
    xAxisLabel: str
    y1AxisLabel: str
    description: str  # <--- ADD THIS LINE
    data: List[GraphDataPoint]