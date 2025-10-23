from pydantic import BaseModel
from typing import List, Optional

# --- Pydantic Models ---

class GraphRequest(BaseModel):
    prompt: str

class GraphDataPoint(BaseModel):
    x: str  # This will always be the date
    y1: Optional[float] = None  # Primary value (can be null)
    y2: Optional[float] = None  # Secondary value (can be null)

class GraphResponse(BaseModel):
    xAxisLabel: str
    y1AxisLabel: str            # Label for y1
    y2AxisLabel: Optional[str] = None # Label for y2 (if it exists)
    description: str            # Factual summary
    data: List[GraphDataPoint]