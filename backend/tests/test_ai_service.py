import pytest
from api.ai_service import (
    agent_extract_clauses,
    agent_analyze_risk,
    agent_generate_recommendation,
    agent_compliance_check,
    agent_compare_versions,
    agent_chat_router,
    agent_chat_answer
)
from api.models import (
    ExtractedClauses,
    RiskAnalysis,
    RecommendationOutput,
    ComplianceOutput,
    ComparisonResult,
    ChatResponse
)

@pytest.fixture
def mock_ai(mocker):
    # This fixture allows tests to easily set the return value of model.invoke
    def _mock_ai(return_value):
        mock_model = mocker.MagicMock()
        mock_structured = mocker.MagicMock()
        # mock_structured is the runnable chain returned by with_structured_output
        mock_model.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = return_value
        mock_structured.return_value = return_value # in case LCEL calls it as a function
        
        # for agents that don't use structured output (if any) or just use model.invoke directly
        mock_model.invoke.return_value = mocker.MagicMock(content="Mocked Content")
        mocker.patch("api.ai_service.get_ai_model", return_value=mock_model)
    return _mock_ai

def test_agent_extract_clauses(mock_ai):
    mock_res = ExtractedClauses(important_clauses=[])
    mock_ai(mock_res)
    
    res = agent_extract_clauses("Some policy")
    assert len(res.important_clauses) == 0

def test_agent_analyze_risk(mock_ai):
    mock_res = RiskAnalysis(summary="Test", risk_score=5.0, risk_level="Medium")
    mock_ai(mock_res)
    
    res = agent_analyze_risk([])
    assert res.risk_score == 5.0
    assert res.risk_level == "Medium"

def test_agent_chat_router(mocker, mock_ai):
    # Chat router expects an object with needs_rag attribute
    mock_router_res = mocker.MagicMock(needs_rag=True)
    mock_ai(mock_router_res)
    
    res = agent_chat_router("Is this GDPR compliant?")
    assert res is True
