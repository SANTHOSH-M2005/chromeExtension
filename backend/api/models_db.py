from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import datetime
from api.database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    preferences = relationship("UserPreferenceDB", back_populates="user", uselist=False)
    histories = relationship("AnalysisHistoryDB", back_populates="user")

class UserPreferenceDB(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location_tracking = Column(String, default="Ask Me")
    personalized_ads = Column(String, default="Ask Me")
    third_party_sharing = Column(String, default="Ask Me")
    data_retention = Column(String, default="Ask Me")
    sensitive_data = Column(String, default="Ask Me")

    user = relationship("UserDB", back_populates="preferences")

class PolicyMetadataDB(Base):
    __tablename__ = "policy_metadata"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    histories = relationship("AnalysisHistoryDB", back_populates="policy")

class AnalysisResultDB(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    risk_score = Column(Float)
    risk_level = Column(String)
    summary = Column(Text)
    compliance_notes = Column(Text)
    recommendation = Column(Text)
    explanation = Column(Text)
    clauses = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    history = relationship("AnalysisHistoryDB", back_populates="result", uselist=False)

class AnalysisHistoryDB(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    policy_id = Column(Integer, ForeignKey("policy_metadata.id"))
    result_id = Column(Integer, ForeignKey("analysis_results.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("UserDB", back_populates="histories")
    policy = relationship("PolicyMetadataDB", back_populates="histories")
    result = relationship("AnalysisResultDB", back_populates="history")

class PolicyAnalysisCacheDB(Base):
    __tablename__ = "policy_analysis_cache"

    id = Column(Integer, primary_key=True, index=True)
    content_hash = Column(String, index=True)
    prefs_hash = Column(String, index=True)
    url = Column(String, nullable=True)
    clauses_data = Column(JSON, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    result_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

