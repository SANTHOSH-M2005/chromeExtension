from typing import TypedDict, List
from api.models import Clause, AnalysisResult

class GraphState(TypedDict, total=False):
    """
    Represents the central state (the "clipboard") of our LangGraph workflow.
    As data moves through the flowchart, nodes read from and write to these fields.
    `total=False` means not all fields need to be present at all times.
    """
    
    # Input Data
    url: str
    title: str
    policy_text: str
    user_preferences: dict
    
    # AI Analysis Data
    summary: str
    risk_score: float
    risk_level: str
    important_clauses: List[Clause]
    compliance_notes: str
    recommendation: str
    explanation: str
    
    # Final Output
    final_response: AnalysisResult
    
    # Version Comparison
    old_clauses: List[Clause]
    comparison: dict
    
    # Error Handling
    errors: str

class ChatGraphState(TypedDict, total=False):
    query: str
    messages: List[dict]
    policy_text: str
    analysis: dict # We'll store it as a dict to be safe in state
    preferences: dict
    
    needs_rag: bool
    legal_context: str
    response: str
    
    errors: str
