import pytest
from api.graph import (
    clause_detection_node,
    compliance_node,
    risk_analysis_node,
    recommendation_node,
    comparison_node,
    generate_result_node,
    route_chat,
    chat_router_node
)
from api.state import GraphState, ChatGraphState
from api.models import Clause

def test_clause_detection_node_error(mocker):
    mocker.patch("api.graph.agent_extract_clauses", side_effect=Exception("Mock error"))
    state: GraphState = {"policy_text": "test"}
    result = clause_detection_node(state)
    assert "errors" in result
    assert "Mock error" in result["errors"]

def test_route_chat():
    assert route_chat({"needs_rag": True}) == "chat_rag"
    assert route_chat({"needs_rag": False}) == "chat_answer"
    assert route_chat({}) == "chat_answer"

def test_comparison_node_no_old_clauses(mocker):
    state: GraphState = {"important_clauses": []}
    result = comparison_node(state)
    assert result == {} # Returns empty dict if no old clauses
    
def test_generate_result_node_with_errors():
    state: GraphState = {"errors": "Some error"}
    result = generate_result_node(state)
    assert result == {}

def test_generate_result_node_success():
    state: GraphState = {
        "summary": "Sum",
        "risk_score": 1.0,
        "risk_level": "Low",
        "important_clauses": [],
        "compliance_notes": "Good",
        "recommendation": "Rec",
        "explanation": "Exp"
    }
    result = generate_result_node(state)
    assert "final_response" in result
    assert result["final_response"].risk_score == 1.0
