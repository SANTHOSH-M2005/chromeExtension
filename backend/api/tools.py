import json
import contextvars
from langchain_core.tools import tool

# ContextVar allows us to store state per-request safely
user_prefs_var = contextvars.ContextVar('user_prefs', default={})

@tool
def get_user_preferences() -> str:
    """Returns the current user's strict privacy preferences. Use this to determine what the user cares about."""
    preferences = user_prefs_var.get()
    if not preferences:
        return json.dumps({
            "location_tracking": "Ask Me",
            "personalized_ads": "Ask Me",
            "third_party_sharing": "Ask Me",
            "data_retention": "Ask Me",
            "sensitive_data": "Ask Me"
        })
    return json.dumps(preferences)

@tool
def calculate_risk_score(base_score: float, risk_factors: int) -> float:
    """Calculates and normalizes the final risk score based on the base score and number of risk factors."""
    # Deterministic python logic, preventing the LLM from making up math!
    normalized = base_score + (risk_factors * 0.5)
    return min(normalized, 10.0)

@tool
def policy_knowledge_search(query: str) -> str:
    """Searches a historical knowledge base for information about previous policy analysis."""
    # Placeholder for future RAG (Retrieval-Augmented Generation) implementation
    return "No relevant historical policy data found at this time."
