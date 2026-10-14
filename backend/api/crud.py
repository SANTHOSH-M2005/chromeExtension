from sqlalchemy.orm import Session
from api.models_db import AnalysisHistoryDB, UserDB, PolicyMetadataDB, AnalysisResultDB, UserPreferenceDB, PolicyAnalysisCacheDB
from api.models import AnalysisResult

def get_or_create_default_user(db: Session):
    user = db.query(UserDB).filter(UserDB.username == "default_user").first()
    if not user:
        user = UserDB(username="default_user")
        db.add(user)
        db.commit()
        db.refresh(user)
        # Create default preferences
        prefs = UserPreferenceDB(user_id=user.id)
        db.add(prefs)
        db.commit()
    return user

def create_analysis_history(db: Session, url: str, title: str, result: AnalysisResult, user_id: int = None):
    if not user_id:
        user = get_or_create_default_user(db)
        user_id = user.id

    # Create Policy Metadata
    db_policy = PolicyMetadataDB(url=url, title=title)
    db.add(db_policy)
    
    # Create Analysis Result
    db_result = AnalysisResultDB(
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        summary=result.summary,
        compliance_notes=result.compliance_notes,
        recommendation=result.recommendation,
        explanation=result.explanation,
        clauses=[c.model_dump() for c in result.important_clauses] if result.important_clauses else None
    )
    db.add(db_result)
    db.commit()
    
    db.refresh(db_policy)
    db.refresh(db_result)

    # Create History Link
    db_history = AnalysisHistoryDB(
        user_id=user_id,
        policy_id=db_policy.id,
        result_id=db_result.id
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return db_history

def get_history(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AnalysisHistoryDB).order_by(AnalysisHistoryDB.created_at.desc()).offset(skip).limit(limit).all()

def get_history_by_id(db: Session, history_id: int):
    return db.query(AnalysisHistoryDB).filter(AnalysisHistoryDB.id == history_id).first()

def delete_history(db: Session, history_id: int):
    db_history = db.query(AnalysisHistoryDB).filter(AnalysisHistoryDB.id == history_id).first()
    if db_history:
        db.delete(db_history)
        db.commit()
    return db_history

def get_cached_analysis(db: Session, content_hash: str, prefs_hash: str):
    return db.query(PolicyAnalysisCacheDB).filter(
        PolicyAnalysisCacheDB.content_hash == content_hash,
        PolicyAnalysisCacheDB.prefs_hash == prefs_hash
    ).order_by(PolicyAnalysisCacheDB.created_at.desc()).first()

def get_cached_clauses(db: Session, content_hash: str):
    entry = db.query(PolicyAnalysisCacheDB).filter(
        PolicyAnalysisCacheDB.content_hash == content_hash,
        PolicyAnalysisCacheDB.clauses_data.isnot(None)
    ).order_by(PolicyAnalysisCacheDB.created_at.desc()).first()
    if entry:
        return entry.clauses_data, entry.compliance_notes
    return None, None

def save_cached_analysis(db: Session, content_hash: str, prefs_hash: str, url: str, clauses: list, compliance_notes: str, result_data: dict):
    # Check if this exact entry already exists
    existing = db.query(PolicyAnalysisCacheDB).filter(
        PolicyAnalysisCacheDB.content_hash == content_hash,
        PolicyAnalysisCacheDB.prefs_hash == prefs_hash
    ).first()
    if existing:
        existing.result_data = result_data
        existing.clauses_data = clauses
        existing.compliance_notes = compliance_notes
        db.commit()
        return existing

    new_cache = PolicyAnalysisCacheDB(
        content_hash=content_hash,
        prefs_hash=prefs_hash,
        url=url,
        clauses_data=clauses,
        compliance_notes=compliance_notes,
        result_data=result_data
    )
    db.add(new_cache)
    db.commit()
    db.refresh(new_cache)
    return new_cache

