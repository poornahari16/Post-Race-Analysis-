from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from pes_utils import compute_pes, suggest_adjustments



app = FastAPI(title="PES Advisor API")

# Request model for manual PES analysis
class ManualInput(BaseModel):
    TirePressure_Front: float
    TirePressure_Rear: float
    TireSize_Front: float
    TireSize_Rear: float
    DriverWeight_kg: float
    CoolantTemperature_C: float

# Response model
class PESOutput(BaseModel):
    estimated_pes: float
    suggestions: List[str]

# Endpoint 1: Analyze custom input
@app.post("/analyze", response_model=PESOutput)
def analyze_manual_input(data: ManualInput):
    row = data.dict()
    row["PES"] = 0  # placeholder

    pes = compute_pes(row)
    suggestions = suggest_adjustments(row)

    return PESOutput(
        estimated_pes=round(pes, 6),
        suggestions=suggestions
    )

# Endpoint 2: Get optimal ranges for all parameters
@app.get("/optimal-ranges")
def get_optimal_ranges() -> Dict[str, Dict[str, float]]:
    return {
        "CoolantTemperature_C": {"min": 85, "max": 95},
        "DriverWeight_kg": {"min": 68, "max": 72},
        "TireSize_Front": {"recommended": 305},
        "TireSize_Rear": {"recommended": 305},
        "TirePressure_Average": {"min": 21.5, "max": 22.5}
    }
