import pytest
from pydantic import ValidationError
from api.models import (
    Clause,
    UserPreferences,
    ClauseChange,
    ComparisonResult,
    AnalysisResult,
    AnalyzeRequest,
    ChatMessage,
    ChatRequest,
    ChatResponse
)

def test_clause_validation():
    # Valid
    c = Clause(name="Test", description="Desc", risk_level="Low", evidence="Text")
    assert c.name == "Test"
    
    # Missing fields
    with pytest.raises(ValidationError):
        Clause(name="Test")

def test_user_preferences_defaults():
    prefs = UserPreferences()
    assert prefs.location_tracking == "Ask Me"
    assert prefs.personalized_ads == "Ask Me"
    
def test_analysis_result_validation():
    # Valid
    res = AnalysisResult(
        summary="Sum",
        risk_score=5.5,
        risk_level="Medium",
        important_clauses=[],
        compliance_notes="Notes",
        recommendation="Rec",
        explanation="Exp"
    )
    assert res.risk_score == 5.5
    assert res.comparison is None
    
    # Invalid risk score type
    with pytest.raises(ValidationError):
        AnalysisResult(
            summary="Sum",
            risk_score="five", # Should fail
            risk_level="Medium",
            important_clauses=[],
            compliance_notes="Notes",
            recommendation="Rec",
            explanation="Exp"
        )

def test_chat_models():
    msg = ChatMessage(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"
    
    req = ChatRequest(
        query="test?",
        messages=[msg],
        policy_text="policy",
        analysis=AnalysisResult(
            summary="Sum",
            risk_score=5.5,
            risk_level="Medium",
            important_clauses=[],
            compliance_notes="Notes",
            recommendation="Rec",
            explanation="Exp"
        ),
        preferences=None
    )
    assert req.query == "test?"
    assert req.preferences is None
