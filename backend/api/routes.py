from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from api.models import AnalyzeRequest, AnalysisResult
from api.graph import app_graph
from api.state import GraphState
from api.tools import user_prefs_var
from api.database import get_db
import api.crud as crud

router = APIRouter()

import re
import hashlib
import json

def get_normalized_content_hash(text: str) -> str:
    cleaned = re.sub(r'\s+', ' ', text.strip().lower())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()

def get_prefs_hash(prefs_dict: dict) -> str:
    if not prefs_dict:
        return "default"
    return hashlib.sha256(json.dumps(prefs_dict, sort_keys=True).encode("utf-8")).hexdigest()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_text(request: AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="The extracted text is empty.")

        # Set the context variable for the tools to read
        if request.preferences:
            user_prefs_var.set(request.preferences.model_dump())
        else:
            user_prefs_var.set({})

        user_prefs_dict = request.preferences.model_dump() if request.preferences else {}
        content_hash = get_normalized_content_hash(request.text)
        prefs_hash = get_prefs_hash(user_prefs_dict)

        # 1. Exact Match Cache: Same content & Same preferences -> 100% Identical Score & Result
        cached_entry = crud.get_cached_analysis(db, content_hash=content_hash, prefs_hash=prefs_hash)
        if cached_entry and cached_entry.result_data:
            print("-> Cache Hit: Returning deterministic cached analysis result.")
            final_response = AnalysisResult.model_validate(cached_entry.result_data)
            crud.create_analysis_history(db=db, url=request.url, title=request.title, result=final_response)
            return final_response

        # 2. Same Content, Different Preferences: Reuse exact same extracted clauses & RAG notes,
        # and deterministically compute the updated risk score and recommendation.
        cached_clauses_data, cached_compliance = crud.get_cached_clauses(db, content_hash=content_hash)
        if cached_clauses_data:
            print("-> Clause Cache Hit: Content matched. Recalculating score deterministically for updated preferences...")
            from api.ai_service import calculate_deterministic_risk_score, agent_generate_recommendation
            from api.models import Clause

            score, level, summary = calculate_deterministic_risk_score(cached_clauses_data, user_prefs_dict)
            rec_output = agent_generate_recommendation(cached_clauses_data, score, level)

            final_response = AnalysisResult(
                summary=summary,
                risk_score=score,
                risk_level=level,
                important_clauses=[c if isinstance(c, Clause) else Clause.model_validate(c) for c in cached_clauses_data],
                compliance_notes=cached_compliance or "No compliance issues detected.",
                recommendation=rec_output.recommendation,
                explanation=rec_output.explanation,
                comparison=None
            )

            crud.save_cached_analysis(
                db=db,
                content_hash=content_hash,
                prefs_hash=prefs_hash,
                url=request.url,
                clauses=[c.model_dump() for c in final_response.important_clauses],
                compliance_notes=final_response.compliance_notes,
                result_data=final_response.model_dump()
            )
            crud.create_analysis_history(db=db, url=request.url, title=request.title, result=final_response)
            return final_response

        # 3. New Policy Content: Run LangGraph Workflow for first-time analysis
        from api.models_db import AnalysisHistoryDB, PolicyMetadataDB
        
        # Check for previous analysis of this URL
        old_history = db.query(AnalysisHistoryDB).join(PolicyMetadataDB).filter(
            PolicyMetadataDB.url == request.url
        ).order_by(AnalysisHistoryDB.created_at.desc()).first()

        old_clauses = None
        if old_history and old_history.result and old_history.result.clauses:
            old_clauses = old_history.result.clauses

        # Create the initial state for the graph
        initial_state: GraphState = {
            "url": request.url,
            "title": request.title,
            "policy_text": request.text,
            "user_preferences": user_prefs_dict,
            "old_clauses": old_clauses
        }

        print("--- Starting LangGraph Workflow for New Content ---")
        final_state = app_graph.invoke(initial_state)

        # Check if any node in the graph reported an error
        if "errors" in final_state and final_state["errors"]:
            raise HTTPException(status_code=500, detail=final_state["errors"])

        final_response: AnalysisResult = final_state["final_response"]
        
        # Save to cache so future analyses of identical or modified preferences are 100% deterministic
        crud.save_cached_analysis(
            db=db,
            content_hash=content_hash,
            prefs_hash=prefs_hash,
            url=request.url,
            clauses=[c.model_dump() for c in final_response.important_clauses],
            compliance_notes=final_response.compliance_notes,
            result_data=final_response.model_dump()
        )

        # Save to database history
        crud.create_analysis_history(db=db, url=request.url, title=request.title, result=final_response)

        # Return the final packaged response
        return final_response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {str(e)}")
        # Catch unexpected errors and return a 500 Server Error
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def read_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    history = crud.get_history(db, skip=skip, limit=limit)
    return [
        {
            "id": h.id,
            "url": h.policy.url if h.policy else None,
            "title": h.policy.title if h.policy else None,
            "risk_score": h.result.risk_score if h.result else None,
            "risk_level": h.result.risk_level if h.result else None,
            "created_at": h.created_at
        } for h in history
    ]

@router.get("/history/{history_id}")
def read_history_item(history_id: int, db: Session = Depends(get_db)):
    h = crud.get_history_by_id(db, history_id=history_id)
    if h is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": h.id,
        "url": h.policy.url if h.policy else None,
        "title": h.policy.title if h.policy else None,
        "result": {
            "summary": h.result.summary if h.result else None,
            "risk_score": h.result.risk_score if h.result else None,
            "risk_level": h.result.risk_level if h.result else None,
            "compliance_notes": h.result.compliance_notes if h.result else None,
            "recommendation": h.result.recommendation if h.result else None,
            "explanation": h.result.explanation if h.result else None
        } if h.result else None,
        "created_at": h.created_at
    }

@router.delete("/history/{history_id}")
def delete_history_item(history_id: int, db: Session = Depends(get_db)):
    db_history = crud.delete_history(db, history_id=history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"status": "success", "message": "Analysis deleted"}

from api.models import ChatRequest, ChatResponse
from api.graph import chat_graph
from api.state import ChatGraphState

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        initial_state: ChatGraphState = {
            "query": request.query,
            "messages": [msg.model_dump() for msg in request.messages],
            "policy_text": request.policy_text,
            "analysis": request.analysis.model_dump(),
            "preferences": request.preferences.model_dump() if request.preferences else {}
        }
        
        print("--- Starting LangGraph Chat Workflow ---")
        final_state = chat_graph.invoke(initial_state)
        
        if "errors" in final_state and final_state["errors"]:
            raise HTTPException(status_code=500, detail=final_state["errors"])
            
        return ChatResponse(response=final_state.get("response", "I could not generate a response."))
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
