from fastapi import FastAPI, HTTPException
from typing import List
from app.models import DealContext, RiskAssessment
from app.mock_data import MOCK_DEALS
from app.engine import evaluate_deal_risk

app = FastAPI(
    title="Mindtickle AI Deal Rescue API",
    description="API Engine for analyzing B2B deal risk and auto-generating manager intervention playbooks.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "Mindtickle AI Deal Intervention Copilot API"}

@app.get("/api/deals", response_model=List[DealContext])
def get_all_deals():
    return [DealContext(**d) for d in MOCK_DEALS]

@app.post("/api/evaluate", response_model=RiskAssessment)
def evaluate_deal(deal: DealContext):
    try:
        return evaluate_deal_risk(deal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))