from pydantic import BaseModel
from typing import List, Optional

class DealContext(BaseModel):
    deal_id: str
    account_name: str
    rep_name: str
    deal_value: float
    stage: str
    days_in_stage: int
    transcript_snippet: str
    additional_notes: Optional[str] = None

class RiskAssessment(BaseModel):
    deal_id: str
    account_name: str
    rep_name: str
    risk_score: int  # 0 to 100
    risk_level: str  # High, Medium, Low
    identified_risks: List[str]
    retrieved_playbook_rules: List[str]
    intervention_playbook: List[str]
    recommended_action: str
    executive_outreach_draft: str