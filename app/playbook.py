from typing import List, Dict

# Knowledge Base representing Enterprise Sales Methodology & Playbooks
SALES_PLAYBOOK_KNOWLEDGE_BASE: List[Dict[str, any]] = [
    {
        "id": "RULE-MEDDPICC-01",
        "category": "MEDDPICC - Champion Churn",
        "keywords": ["champion", "left", "departed", "new lead", "turnover", "resigned", "replaced"],
        "guideline": "When a primary internal champion leaves or is replaced, deal risk automatically escalates to High (>80). Required Action: Schedule a Director-to-Director alignment call within 5 business days and re-map key decision stakeholders."
    },
    {
        "id": "RULE-MEDDPICC-02",
        "category": "MEDDPICC - Economic Buyer & Budget",
        "keywords": ["budget", "freeze", "cuts", "pricing", "cost", "30%", "lower", "expensive", "discount"],
        "guideline": "If budget cuts or competitor price undercutting (>20% difference) are raised, do not offer immediate discounts. Required Action: Offer flexible payment terms, modular feature packaging, and schedule a Manager commercial review."
    },
    {
        "id": "RULE-TECH-03",
        "category": "Technical & Engineering Blockers",
        "keywords": ["engineering", "bandwidth", "resource", "sso", "implementation", "soc2", "security", "infosec", "delay"],
        "guideline": "When technical implementation bandwidth or security review delays emerge, engage Solutions Architecture immediately. Required Action: Offer complimentary implementation support hours and provide pre-approved SOC2 compliance packages."
    },
    {
        "id": "RULE-VELOCITY-04",
        "category": "Pipeline Stagnation",
        "keywords": ["stalled", "days", "slips", "ghosting", "no reply", "unresponsive"],
        "guideline": "Deals remaining in 'Proposal Sent' or 'Decision Pending' for >14 days require proactive manager intervention to prevent quarter-end slippage."
    }
]

def retrieve_playbook_context(transcript_text: str, days_in_stage: int) -> List[Dict[str, str]]:
    """
    RAG Retriever: Queries the sales playbook knowledge base using keyword and metadata heuristics.
    Returns matched sales methodology rules to ground the LLM evaluation.
    """
    matched_rules = []
    text_lower = transcript_text.lower()
    
    for rule in SALES_PLAYBOOK_KNOWLEDGE_BASE:
        if any(keyword in text_lower for keyword in rule["keywords"]):
            matched_rules.append(rule)
            
    # Metadata-driven retrieval trigger
    if days_in_stage > 14 and not any(r["id"] == "RULE-VELOCITY-04" for r in matched_rules):
        matched_rules.append(SALES_PLAYBOOK_KNOWLEDGE_BASE[3])
        
    return matched_rules