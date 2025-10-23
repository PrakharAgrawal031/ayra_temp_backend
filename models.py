from pydantic import BaseModel
from typing import List, Optional

# --- Pydantic Models ---

class GraphRequest(BaseModel):
    prompt: str

class GraphDataPoint(BaseModel):
    x: str  # This will always be the date
    y1: Optional[float] = None  # Primary value (can be null)
    y2: Optional[float] = None  # Secondary value (can be null)

# models.py
class GraphResponse(BaseModel):
    xAxisLabel: str
    y1AxisLabel: str
    y2AxisLabel: Optional[str] = None
    y1AxisMin: Optional[float] = None  # <--- ADD THIS
    y1AxisMax: Optional[float] = None  # <--- ADD THIS
    y2AxisMin: Optional[float] = None  # <--- ADD THIS
    y2AxisMax: Optional[float] = None  # <--- ADD THIS
    description: str
    data: List[GraphDataPoint]