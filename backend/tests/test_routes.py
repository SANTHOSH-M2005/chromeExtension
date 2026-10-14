import pytest
from fastapi.testclient import TestClient
from main import app
from api.models import AnalysisResult, ChatResponse

client = TestClient(app)

def test_analyze_empty_text():
    response = client.post(
        "/api/analyze",
        json={
            "url": "http://test.com",
            "title": "Test Title",
            "text": "   ",
            "preferences": None
        }
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]

def test_analyze_graph_error(mocker):
    # Mock the graph to return an error
    mocker.patch("api.routes.app_graph.invoke", return_value={"errors": "Mock graph error"})
    
    from api.database import get_db
    def override_get_db():
        mock_db = mocker.MagicMock()
        mock_db.query().join().filter().order_by().first.return_value = None
        yield mock_db
    app.dependency_overrides[get_db] = override_get_db

    response = client.post(
        "/api/analyze",
        json={
            "url": "http://test.com",
            "title": "Test Title",
            "text": "Some text",
            "preferences": None
        }
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Mock graph error"
    app.dependency_overrides.clear()

def test_analyze_success(mocker):
    # Mock DB operations
    mocker.patch("api.routes.crud.create_analysis_history", return_value=None)
    mocker.patch("api.routes.Session", autospec=True)
    
    # Mock the graph to return a successful state
    mock_res = AnalysisResult(
        summary="Sum",
        risk_score=1.0,
        risk_level="Low",
        important_clauses=[],
        compliance_notes="Good",
        recommendation="Rec",
        explanation="Exp"
    )
    mocker.patch("api.routes.app_graph.invoke", return_value={"final_response": mock_res})
    
    # We must patch get_db dependency if it connects to postgres. 
    # The TestClient uses the real dependency unless overridden.
    # To keep it simple, we patch db query in the route.
    mocker.patch("api.routes.crud.get_history", return_value=[])
    
    # Let's override the DB dependency for the test
    from api.database import get_db
    def override_get_db():
        mock_db = mocker.MagicMock()
        mock_db.query().join().filter().order_by().first.return_value = None
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    response = client.post(
        "/api/analyze",
        json={
            "url": "http://test.com",
            "title": "Test Title",
            "text": "Some text",
            "preferences": None
        }
    )
    
    assert response.status_code == 200
    assert response.json()["summary"] == "Sum"
    
    app.dependency_overrides.clear()

def test_chat_success(mocker):
    mocker.patch("api.routes.chat_graph.invoke", return_value={"response": "Chat AI answer"})
    
    response = client.post(
        "/api/chat",
        json={
            "query": "Hello",
            "messages": [],
            "policy_text": "text",
            "analysis": {
                "summary": "Sum",
                "risk_score": 1.0,
                "risk_level": "Low",
                "important_clauses": [],
                "compliance_notes": "Good",
                "recommendation": "Rec",
                "explanation": "Exp"
            },
            "preferences": None
        }
    )
    assert response.status_code == 200
    assert response.json()["response"] == "Chat AI answer"
