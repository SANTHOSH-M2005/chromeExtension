import os
import pytest

# Set env vars BEFORE importing anything that might initialize connections
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["AI_API_KEY"] = "test_key"
os.environ["AI_BASE_URL"] = "http://test_url"

from api.models_db import Base

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    from api.database import engine
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

