import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models_db import Base, AnalysisHistoryDB, PolicyMetadataDB
from api.models import AnalysisResult, Clause
from api.crud import create_analysis_history, get_history, get_history_by_id, delete_history

# Setup in-memory sqlite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_and_get_history(db):
    res = AnalysisResult(
        summary="Test Summary",
        risk_score=5.0,
        risk_level="Medium",
        important_clauses=[
            Clause(name="Clause 1", description="Desc 1", risk_level="Low", evidence="Ev 1")
        ],
        compliance_notes="Notes",
        recommendation="Rec",
        explanation="Exp",
        comparison=None
    )
    
    # Create history
    h = create_analysis_history(db, url="http://test.com", title="Test Title", result=res)
    assert h.id is not None
    assert h.policy.url == "http://test.com"
    
    # Get history
    history_list = get_history(db)
    assert len(history_list) == 1
    assert history_list[0].result.summary == "Test Summary"
    
def test_delete_history(db):
    res = AnalysisResult(
        summary="Test Summary",
        risk_score=5.0,
        risk_level="Medium",
        important_clauses=[],
        compliance_notes="Notes",
        recommendation="Rec",
        explanation="Exp",
        comparison=None
    )
    h = create_analysis_history(db, url="http://test.com", title="Test Title", result=res)
    assert h.id is not None
    
    # Delete it
    deleted = delete_history(db, h.id)
    assert deleted is not None
    assert deleted.id == h.id
    
    # Verify deletion
    h2 = get_history_by_id(db, h.id)
    assert h2 is None
