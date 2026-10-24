import os
import json
from groq import Groq
from app.models import DealContext, RiskAssessment
from app.playbook import retrieve_playbook_context

SYSTEM_PROMPT = """
You are an AI Deal Rescue & Sales Intervention Engine for Sales Managers.
Analyze the provided deal context, call transcript snippet, and RETRIEVED SALES PLAYBOOK GUIDELINES.

Use the retrieved playbook guidelines as your strict grounding reference to determine the deal risk score (0-100) and construct a step-by-step manager intervention playbook.

Return ONLY a valid JSON object matching this schema:
{
  "risk_score": <int 0-100>,
  "risk_level": "<High|Medium|Low>",
  "identified_risks": ["<risk 1>", "<risk 2>"],
  "intervention_playbook": ["<step 1>", "<step 2>"],
  "recommended_action": "<single high-impact priority action for the manager>",
  "executive_outreach_draft": "<short 3-sentence email draft for manager to send to buyer VP>"
}
"""

def evaluate_deal_risk(deal: DealContext) -> RiskAssessment:
    # 1. RAG Retrieval Step
    matched_rules = retrieve_playbook_context(deal.transcript_snippet, deal.days_in_stage)
    
    rule_summaries = [f"[{r['category']}] {r['guideline']}" for r in matched_rules]
    rag_context_str = "\n".join(rule_summaries) if rule_summaries else "Standard sales execution rules apply."

    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # Fallback Execution (If API Key is missing or invalid)
    if not groq_api_key or groq_api_key == "mock-key":
        is_high_risk = deal.days_in_stage > 14 or len(matched_rules) > 0
        return RiskAssessment(
            deal_id=deal.deal_id,
            account_name=deal.account_name,
            rep_name=deal.rep_name,
            risk_score=85 if is_high_risk else 25,
            risk_level="High" if is_high_risk else "Low",
            identified_risks=[
                "Detected commercial or technical friction in call transcript",
                f"Grounded Alert: Triggered {len(matched_rules)} Sales Playbook Policy Rule(s)"
            ],
            retrieved_playbook_rules=rule_summaries if rule_summaries else ["Standard pipeline monitoring"],
            intervention_playbook=rule_summaries if rule_summaries else ["Continue weekly pipeline reviews"],
            recommended_action="Execute immediate Manager 1:1 intervention based on retrieved playbook guidelines.",
            executive_outreach_draft=f"Hi {deal.account_name} Leadership, following up on our recent technical discussion to ensure our solutions engineering team addresses your bandwidth requirements. Let me know if a quick 10-minute check-in works."
        )

    # 2. Production RAG LLM Execution via Groq
    try:
        client = Groq(api_key=groq_api_key)
        
        user_content = f"""
DEAL METRICS:
- Account: {deal.account_name}
- Sales Rep: {deal.rep_name}
- Stage: {deal.stage} ({deal.days_in_stage} days)
- Deal Value: ${deal.deal_value:,.2f}
- Additional Notes: {deal.additional_notes or 'None'}

CALL TRANSCRIPT / SUMMARY:
"{deal.transcript_snippet}"

RETRIEVED SALES PLAYBOOK GUIDELINES (RAG CONTEXT):
{rag_context_str}
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1
        )
        
        res_data = json.loads(response.choices[0].message.content)
        
        return RiskAssessment(
            deal_id=deal.deal_id,
            account_name=deal.account_name,
            rep_name=deal.rep_name,
            risk_score=res_data.get("risk_score", 50),
            risk_level=res_data.get("risk_level", "Medium"),
            identified_risks=res_data.get("identified_risks", []),
            retrieved_playbook_rules=rule_summaries,
            intervention_playbook=res_data.get("intervention_playbook", []),
            recommended_action=res_data.get("recommended_action", "Follow up with rep."),
            executive_outreach_draft=res_data.get("executive_outreach_draft", "")
        )
    except Exception as e:
        # Graceful fallback on API or JSON parsing errors
        is_high_risk = deal.days_in_stage > 14 or len(matched_rules) > 0
        return RiskAssessment(
            deal_id=deal.deal_id,
            account_name=deal.account_name,
            rep_name=deal.rep_name,
            risk_score=85 if is_high_risk else 25,
            risk_level="High" if is_high_risk else "Low",
            identified_risks=[
                f"API Fallback Triggered: {str(e)}",
                f"Grounded Alert: Triggered {len(matched_rules)} Sales Playbook Policy Rule(s)"
            ],
            retrieved_playbook_rules=rule_summaries if rule_summaries else ["Standard pipeline monitoring"],
            intervention_playbook=rule_summaries if rule_summaries else ["Continue weekly pipeline reviews"],
            recommended_action="Execute immediate Manager 1:1 intervention based on retrieved playbook guidelines.",
            executive_outreach_draft=f"Hi {deal.account_name} Leadership, following up on our recent technical discussion to ensure our solutions engineering team addresses your bandwidth requirements."
        )