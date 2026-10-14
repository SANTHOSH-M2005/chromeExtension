import os
import json
from langchain_openai import ChatOpenAI
from api.prompts import clause_detection_prompt, risk_analysis_prompt, recommendation_prompt, compliance_prompt
from api.models import ExtractedClauses, RiskAnalysis, RecommendationOutput, ComplianceOutput

def _serialize_clauses(clauses: list) -> str:
    """Helper function to serialize clause objects to JSON strings for AI prompts."""
    # Handle cases where clauses might already be dicts or Pydantic models
    return json.dumps([c if isinstance(c, dict) else c.model_dump() for c in clauses], indent=2)

import hashlib

# In-memory cache for clause extraction to guarantee 100% deterministic results for identical text
_clause_cache: dict = {}

def get_ai_model():
    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    
    if not api_key or not base_url:
        raise ValueError("AI_API_KEY or AI_BASE_URL is missing from the environment variables.")
        
    model_name = os.getenv("AI_MODEL", "gpt-3.5-turbo")
    
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0.0
    )

def agent_extract_clauses(text: str) -> ExtractedClauses:
    """Agent 1: Extracts structured clauses from the raw text with caching."""
    text_cleaned = text.strip()
    text_hash = hashlib.sha256(text_cleaned.encode("utf-8")).hexdigest()
    if text_hash in _clause_cache:
        return _clause_cache[text_hash]

    model = get_ai_model()
    structured_model = model.with_structured_output(ExtractedClauses)
    chain = clause_detection_prompt | structured_model
    result = chain.invoke({"policy_text": text_cleaned})
    _clause_cache[text_hash] = result
    return result

def agent_compliance_check(clauses: list, legal_text: str) -> ComplianceOutput:
    """Agent 1.5: Checks clauses against retrieved legal text (RAG)."""
    model = get_ai_model()
    structured_model = model.with_structured_output(ComplianceOutput)
    chain = compliance_prompt | structured_model
    clauses_json = _serialize_clauses(clauses)
    return chain.invoke({
        "clauses_json": clauses_json,
        "legal_text": legal_text
    })

def calculate_deterministic_risk_score(clauses: list, preferences: dict = None) -> tuple[float, str, str]:
    """
    Deterministically computes the risk score based on:
    1. Base clause severity (Critical, High, Medium, Low)
    2. User Privacy Preferences:
       - 'Do Not Allow': Heavy penalty for detected invasive practices (+16-18 pts)
       - 'Ask Me': Moderate caution penalty (+4-5 pts)
       - 'Allow': Consent discount (-8 pts, reduces risk score since user explicitly opted in)
    """
    if not clauses:
        return 2.0, "Low", "No privacy risk clauses detected in this document."

    if preferences is None:
        preferences = {}

    loc_pref = preferences.get("location_tracking", "Ask Me")
    ads_pref = preferences.get("personalized_ads", "Ask Me")
    share_pref = preferences.get("third_party_sharing", "Ask Me")
    ret_pref = preferences.get("data_retention", "Ask Me")
    sens_pref = preferences.get("sensitive_data", "Ask Me")

    clause_texts = []
    crit_count = 0
    high_count = 0
    med_count = 0
    low_count = 0

    for c in clauses:
        level = (c.get("risk_level") if isinstance(c, dict) else c.risk_level).lower()
        if level in ("critical", "severe"):
            crit_count += 1
        elif level == "high":
            high_count += 1
        elif level == "medium":
            med_count += 1
        else:
            low_count += 1

        name = (c.get("name") if isinstance(c, dict) else c.name).lower()
        desc = (c.get("description") if isinstance(c, dict) else c.description).lower()
        evidence = (c.get("evidence") if isinstance(c, dict) else c.evidence).lower()
        clause_texts.append(f"{name} {desc} {evidence}")

    all_text = " ".join(clause_texts)

    # Base severity calibration
    if crit_count > 0:
        base_points = 55.0 + (crit_count - 1) * 8.0 + high_count * 5.0 + med_count * 2.0
    elif high_count > 0:
        base_points = 45.0 + (high_count - 1) * 6.0 + med_count * 3.0
    elif med_count > 0:
        base_points = 28.0 + (med_count - 1) * 4.0 + low_count * 1.5
    else:
        base_points = 15.0 + low_count * 2.0

    pref_adjustments = 0.0
    flagged_reasons = []

    # 1. Location Tracking
    if any(k in all_text for k in ("location", "gps", "geo", "geolocation", "beacon", "coordinates", "tracking", "cross-device")):
        if loc_pref == "Do Not Allow":
            pref_adjustments += 16.0
            flagged_reasons.append("violates your strict preference against location tracking")
        elif loc_pref == "Ask Me":
            pref_adjustments += 4.0
        elif loc_pref == "Allow":
            pref_adjustments -= 8.0

    # 2. Personalized Advertising
    if any(k in all_text for k in ("personalized ad", "ad network", "targeted ad", "advertising", "ad broker", "commercialize", "profiling", "telemetry")):
        if ads_pref == "Do Not Allow":
            pref_adjustments += 16.0
            flagged_reasons.append("violates your preference against personalized advertising")
        elif ads_pref == "Ask Me":
            pref_adjustments += 4.0
        elif ads_pref == "Allow":
            pref_adjustments -= 8.0

    # 3. Third-Party Sharing
    if any(k in all_text for k in ("third-party", "third party", "sharing", "data broker", "affiliate", "sell", "transfer", "disclose", "syndicate")):
        if share_pref == "Do Not Allow":
            pref_adjustments += 16.0
            flagged_reasons.append("violates your preference against third-party data sharing")
        elif share_pref == "Ask Me":
            pref_adjustments += 4.0
        elif share_pref == "Allow":
            pref_adjustments -= 8.0

    # 4. Data Retention & AI
    if any(k in all_text for k in ("retention", "indefinitely", "perpetual", "ai training", "retain", "machine learning", "training", "stored permanently")):
        if ret_pref == "Do Not Allow":
            pref_adjustments += 16.0
            flagged_reasons.append("violates your preference against indefinite data retention")
        elif ret_pref == "Ask Me":
            pref_adjustments += 4.0
        elif ret_pref == "Allow":
            pref_adjustments -= 8.0

    # 5. Sensitive Data & Device Hardware
    if any(k in all_text for k in ("biometric", "health", "financial", "clipboard", "bluetooth", "peripheral", "sensitive", "minor", "children", "arbitration")):
        if sens_pref == "Do Not Allow":
            pref_adjustments += 18.0
            flagged_reasons.append("violates your preference against sensitive data processing")
        elif sens_pref == "Ask Me":
            pref_adjustments += 5.0
        elif sens_pref == "Allow":
            pref_adjustments -= 8.0

    raw_total = base_points + pref_adjustments
    # Scale raw total to 1.0 - 10.0
    scaled_score = max(1.5, min(9.8, raw_total / 10.0))
    risk_score = round(scaled_score, 1)

    if risk_score >= 7.5:
        risk_level = "High"
    elif risk_score >= 4.5:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if flagged_reasons:
        summary = f"This policy presents {risk_level.lower()} privacy risks and directly {', and '.join(flagged_reasons)}."
    else:
        summary = f"This policy presents an overall {risk_level.lower()} privacy risk based on detected clauses and your chosen privacy preferences."

    return risk_score, risk_level, summary

def agent_analyze_risk(clauses: list, preferences: dict = None) -> RiskAnalysis:
    """Agent 2: Analyzes risk deterministically based on clauses and user preferences."""
    score, level, summary = calculate_deterministic_risk_score(clauses, preferences)
    return RiskAnalysis(
        summary=summary,
        risk_score=score,
        risk_level=level
    )

from api.tools import get_user_preferences, calculate_risk_score, policy_knowledge_search

def agent_generate_recommendation(clauses: list, risk_score: float, risk_level: str) -> RecommendationOutput:
    """Agent 3: Recommends an action, pausing to call tools (like getting user preferences) if needed."""
    model = get_ai_model()
    
    # 1. Give the AI permission to use our tools
    tools = [get_user_preferences, calculate_risk_score, policy_knowledge_search]
    model_with_tools = model.bind_tools(tools)
    
    clauses_json = _serialize_clauses(clauses)
    
    # 2. Ask the model what it wants to do
    chain = recommendation_prompt | model_with_tools
    response = chain.invoke({
        "risk_score": risk_score,
        "risk_level": risk_level,
        "clauses_json": clauses_json
    })
    
    # We need to build a message history so the model remembers the context after using the tool
    messages = [
        {"role": "system", "content": recommendation_prompt.messages[0].prompt.template},
        {"role": "user", "content": recommendation_prompt.messages[1].prompt.template.format(
            risk_score=risk_score, risk_level=risk_level, clauses_json=clauses_json
        )},
        response # The AI's request to call a tool
    ]
    
    # 3. Check if the AI decided to call a tool
    if response.tool_calls:
        print(f"-> Agent 3 decided to use tools: {[tc['name'] for tc in response.tool_calls]}")
        
        # Execute the tools and append the results to the message history
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            tool_result = ""
            if tool_name == "get_user_preferences":
                tool_result = get_user_preferences.invoke(tool_args)
            elif tool_name == "calculate_risk_score":
                tool_result = calculate_risk_score.invoke(tool_args)
            elif tool_name == "policy_knowledge_search":
                tool_result = policy_knowledge_search.invoke(tool_args)
                
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": str(tool_result)
            })
            
    # 4. Call the model again, but this time force it to output our final Pydantic Schema
    structured_model = model.with_structured_output(RecommendationOutput)
    final_response = structured_model.invoke(messages)
    
    return final_response

from api.models import ComparisonResult
from api.prompts import comparison_prompt

def agent_compare_versions(old_clauses: list, new_clauses: list) -> ComparisonResult:
    """Agent 4: Compares old clauses with new clauses."""
    model = get_ai_model()
    structured_model = model.with_structured_output(ComparisonResult)
    chain = comparison_prompt | structured_model
    
    old_json = _serialize_clauses(old_clauses)
    new_json = _serialize_clauses(new_clauses)
    
    return chain.invoke({
        "old_clauses_json": old_json,
        "new_clauses_json": new_json
    })

from pydantic import BaseModel
from api.prompts import chat_router_prompt, chat_answer_prompt
from api.models import ChatResponse

class RouterOutput(BaseModel):
    needs_rag: bool

def agent_chat_router(query: str) -> bool:
    """Agent 5: Chat Router. Decides if RAG is needed."""
    model = get_ai_model()
    structured_model = model.with_structured_output(RouterOutput)
    chain = chat_router_prompt | structured_model
    try:
        res = chain.invoke({"query": query})
        return res.needs_rag
    except:
        return False

def agent_chat_answer(state_data: dict) -> ChatResponse:
    """Agent 6: Chat Answer. Generates the final answer."""
    model = get_ai_model()
    structured_model = model.with_structured_output(ChatResponse)
    chain = chat_answer_prompt | structured_model
    
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state_data.get("messages", [])])
    
    return chain.invoke({
        "query": state_data.get("query", ""),
        "policy_text": state_data.get("policy_text", ""),
        "analysis_json": json.dumps(state_data.get("analysis", {}), indent=2),
        "preferences_json": json.dumps(state_data.get("preferences", {}), indent=2),
        "legal_context": state_data.get("legal_context", "None"),
        "history_text": history_text
    })
