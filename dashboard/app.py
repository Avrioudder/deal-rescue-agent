import sys
import os
from pathlib import Path

# Add project root directory to Python path for Streamlit Cloud imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from app.mock_data import MOCK_DEALS
from app.engine import evaluate_deal_risk
from app.models import DealContext

st.set_page_config(page_title="Mindtickle AI Deal Copilot", layout="wide", page_icon="🎯")

st.title("🎯 Mindtickle AI Deal Rescue & Intervention Copilot")
st.caption("RAG-Powered Sales Manager Workspace for Call Transcript Risk Diagnostics & Automated Playbooks")

# Sidebar - Filter & Interactive Upload Form
st.sidebar.header("⚙️ Manager Controls")
risk_filter = st.sidebar.multiselect("Filter Pipeline by Risk", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])

st.sidebar.markdown("---")
st.sidebar.header("📥 Upload / Analyze Call Transcript")
st.sidebar.caption("Paste a transcript or upload a call log along with key deal metadata.")

with st.sidebar.form("upload_call_form"):
    uploaded_file = st.file_uploader("Upload Call Transcript (.txt)", type=["txt"])
    account_input = st.text_input("Account Name", value="Apex Technologies")
    rep_input = st.text_input("Sales Rep Name", value="Sarah Jenkins")
    value_input = st.number_input("Deal Value ($)", value=140000, step=10000)
    stage_input = st.selectbox("Current Stage", ["Discovery", "Proposal Sent", "Security Review", "Decision Pending"])
    days_input = st.number_input("Days in Stage", value=16)
    notes_input = st.text_input("Additional Context / Notes", value="Procurement involved early.")
    
    pasted_transcript = st.text_area("Or Paste Call Transcript / Email Text", height=120, placeholder="Paste call dialogue or customer email here...")
    
    submit_call = st.form_submit_button("⚡ Run RAG Risk Analysis")

# Handle Form Submission (File or Text Input)
if submit_call:
    final_transcript = ""
    if uploaded_file is not None:
        final_transcript = uploaded_file.read().decode("utf-8")
    elif pasted_transcript.strip():
        final_transcript = pasted_transcript.strip()
        
    if final_transcript:
        adhoc_deal = DealContext(
            deal_id="DEAL-UPLOADED",
            account_name=account_input,
            rep_name=rep_input,
            deal_value=float(value_input),
            stage=stage_input,
            days_in_stage=int(days_input),
            transcript_snippet=final_transcript,
            additional_notes=notes_input
        )
        with st.spinner("Analyzing call transcript using RAG Engine..."):
            assessment = evaluate_deal_risk(adhoc_deal)
            st.session_state["selected_deal"] = adhoc_deal.model_dump()
            st.session_state["selected_eval"] = assessment.model_dump()
            st.sidebar.success(f"Analysis complete for {account_input}!")
    else:
        st.sidebar.warning("Please upload a file or paste transcript text.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 CRM Pipeline Overview")
    for deal_dict in MOCK_DEALS:
        deal = DealContext(**deal_dict)
        assessment = evaluate_deal_risk(deal)
        assessment_dict = assessment.model_dump()
        risk_lvl = assessment_dict.get("risk_level", "Medium")
        
        if risk_lvl in risk_filter:
            with st.expander(f"**{deal.account_name}** | ${deal.deal_value:,.0f} | Risk: {assessment_dict.get('risk_score', 50)}/100 ({risk_lvl})"):
                st.write(f"**Rep:** {deal.rep_name} | **Stage:** {deal.stage} ({deal.days_in_stage} days)")
                st.write(f"**Call Snippet:** *\"{deal.transcript_snippet}\"*")
                if deal.additional_notes:
                    st.write(f"**Notes:** {deal.additional_notes}")
                if st.button(f"View Playbook for {deal.account_name}", key=deal.deal_id):
                    st.session_state["selected_deal"] = deal.model_dump()
                    st.session_state["selected_eval"] = assessment_dict

with col2:
    st.subheader("⚡ Grounded Manager Intervention Playbook")
    if "selected_eval" in st.session_state:
        eval_data = st.session_state["selected_eval"]
        
        st.markdown(f"### Account: **{eval_data.get('account_name', 'Unknown')}** (Rep: **{eval_data.get('rep_name', 'Unknown')}**)")
        st.metric(label="Calculated Deal Risk Score", value=f"{eval_data.get('risk_score', 0)} / 100", delta=eval_data.get('risk_level', 'Low'), delta_color="inverse")
        
        st.write("#### 🔍 Identified Red Flags:")
        for risk in eval_data.get("identified_risks", []):
            st.error(f"• {risk}")
            
        st.write("#### 📚 Retrieved RAG Playbook Rules (Grounding Context):")
        rules = eval_data.get("retrieved_playbook_rules", [])
        if rules:
            for rule in rules:
                st.warning(f"📖 {rule}")
        else:
            st.info("Standard sales execution rules apply.")
            
        st.write("#### 🛠️ Step-by-Step Manager Intervention Playbook:")
        for step in eval_data.get("intervention_playbook", []):
            st.info(f"✔ {step}")
            
        st.write("#### 💡 Recommended Immediate Action:")
        st.success(eval_data.get("recommended_action", "Review pipeline stage velocity."))
            
        st.write("#### ✉️ Executive Sponsor Email Draft (Manager to Buyer Leadership):")
        st.code(eval_data.get("executive_outreach_draft", ""), language="text")
    else:
        st.info("Select a deal from the pipeline overview on the left or upload a call transcript in the sidebar to view the RAG intervention playbook.")