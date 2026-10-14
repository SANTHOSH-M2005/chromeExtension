from langgraph.graph import StateGraph, START, END
from api.state import GraphState
from api.ai_service import agent_extract_clauses, agent_analyze_risk, agent_generate_recommendation, agent_compliance_check
from api.rag_service import get_relevant_laws
from api.models import AnalysisResult

def clause_detection_node(state: GraphState) -> GraphState:
    """Agent 1: Extracts clauses from the text"""
    try:
        print("-> Agent 1: Detecting Clauses...")
        result = agent_extract_clauses(state["policy_text"])
        return {"important_clauses": result.important_clauses}
    except Exception as e:
        return {"errors": f"Clause Detection failed: {e}"}

def compliance_node(state: GraphState) -> GraphState:
    """Agent 1.5: Compliance Agent (RAG)"""
    if "errors" in state: return {}
    try:
        print("-> Agent 1.5: Running Compliance Check (RAG)...")
        clauses = state.get("important_clauses", [])
        if not clauses:
            return {"compliance_notes": "No clauses to analyze."}
            
        # 1. Similarity Search (RAG)
        # We query the vector DB using the first clause's description as a sample query
        query = clauses[0].description
        legal_text = get_relevant_laws(query)
        
        # 2. Compliance AI Analysis
        result = agent_compliance_check(clauses, legal_text)
        return {"compliance_notes": result.compliance_notes}
    except Exception as e:
        return {"errors": f"Compliance Agent failed: {e}"}

def risk_analysis_node(state: GraphState) -> GraphState:
    """Agent 2: Analyzes the overall risk based on clauses and user preferences"""
    if "errors" in state: return {}
    try:
        print("-> Agent 2: Analyzing Risk deterministically with user preferences...")
        clauses = state.get("important_clauses", [])
        preferences = state.get("user_preferences", {})
        result = agent_analyze_risk(clauses, preferences)
        return {
            "summary": result.summary,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level
        }
    except Exception as e:
        return {"errors": f"Risk Analysis failed: {e}"}

def recommendation_node(state: GraphState) -> GraphState:
    """Agent 3: Provides a recommendation based on risk and clauses"""
    if "errors" in state: return {}
    try:
        print("-> Agent 3: Generating Recommendation...")
        result = agent_generate_recommendation(
            state.get("important_clauses", []),
            state.get("risk_score", 0.0),
            state.get("risk_level", "Unknown")
        )
        return {
            "recommendation": result.recommendation,
            "explanation": result.explanation
        }
    except Exception as e:
        return {"errors": f"Recommendation failed: {e}"}

def comparison_node(state: GraphState) -> GraphState:
    """Agent 4: Compares old and new clauses if old clauses are present"""
    if "errors" in state: return {}
    
    old_clauses = state.get("old_clauses")
    if not old_clauses:
        return {} # No comparison needed
        
    try:
        print("-> Agent 4: Comparing Versions...")
        from api.ai_service import agent_compare_versions
        result = agent_compare_versions(
            old_clauses,
            state.get("important_clauses", [])
        )
        return {"comparison": result}
    except Exception as e:
        # Don't fail the whole graph if comparison fails, just print it
        print(f"Comparison failed: {e}")
        return {}

def generate_result_node(state: GraphState) -> GraphState:
    """Final Packager: Combines state into AnalysisResult"""
    if "errors" in state: return {}
    
    print("-> Packager: Building Final Response...")
    final = AnalysisResult(
        summary=state.get("summary", "No summary provided."),
        risk_score=state.get("risk_score", 0.0),
        risk_level=state.get("risk_level", "Unknown"),
        important_clauses=state.get("important_clauses", []),
        compliance_notes=state.get("compliance_notes", "No compliance issues detected."),
        recommendation=state.get("recommendation", "None"),
        explanation=state.get("explanation", "None"),
        comparison=state.get("comparison", None)
    )
    return {"final_response": final}

# ---------------------------------------------------------
# Build the Multi-Agent LangGraph Flowchart
# ---------------------------------------------------------
workflow = StateGraph(GraphState)

# 1. Add the Nodes (The Agents)
workflow.add_node("clause_detection", clause_detection_node)
workflow.add_node("compliance", compliance_node)
workflow.add_node("risk_analysis", risk_analysis_node)
workflow.add_node("recommendation", recommendation_node)
workflow.add_node("comparison", comparison_node)
workflow.add_node("generate_result", generate_result_node)

# 2. Add the Edges (The Flow)
workflow.add_edge(START, "clause_detection")
workflow.add_edge("clause_detection", "compliance")
workflow.add_edge("compliance", "risk_analysis")
workflow.add_edge("risk_analysis", "recommendation")
workflow.add_edge("recommendation", "comparison")
workflow.add_edge("comparison", "generate_result")
workflow.add_edge("generate_result", END)

# 3. Compile the Graph
app_graph = workflow.compile()

# ---------------------------------------------------------
# Chat Graph
# ---------------------------------------------------------
from api.state import ChatGraphState
from api.ai_service import agent_chat_router, agent_chat_answer

def chat_router_node(state: ChatGraphState) -> ChatGraphState:
    """Agent 5: Decides if we need RAG for this question"""
    if "errors" in state: return {}
    try:
        print("-> Chat Router: Analyzing query...")
        needs_rag = agent_chat_router(state.get("query", ""))
        return {"needs_rag": needs_rag}
    except Exception as e:
        return {"errors": f"Chat router failed: {e}"}

def chat_rag_node(state: ChatGraphState) -> ChatGraphState:
    """Agent 5.5: Retrieves laws if needed"""
    if "errors" in state: return {}
    try:
        print("-> Chat RAG: Retrieving legal context...")
        query = state.get("query", "")
        legal_text = get_relevant_laws(query)
        return {"legal_context": legal_text}
    except Exception as e:
        return {"errors": f"Chat RAG failed: {e}"}

def chat_answer_node(state: ChatGraphState) -> ChatGraphState:
    """Agent 6: Generates the answer"""
    if "errors" in state: return {}
    try:
        print("-> Chat Answer: Generating response...")
        result = agent_chat_answer(state)
        return {"response": result.response}
    except Exception as e:
        return {"errors": f"Chat answer failed: {e}"}

def route_chat(state: ChatGraphState):
    if state.get("needs_rag", False):
        return "chat_rag"
    return "chat_answer"

chat_workflow = StateGraph(ChatGraphState)

chat_workflow.add_node("chat_router", chat_router_node)
chat_workflow.add_node("chat_rag", chat_rag_node)
chat_workflow.add_node("chat_answer", chat_answer_node)

chat_workflow.add_edge(START, "chat_router")
chat_workflow.add_conditional_edges("chat_router", route_chat, {
    "chat_rag": "chat_rag",
    "chat_answer": "chat_answer"
})
chat_workflow.add_edge("chat_rag", "chat_answer")
chat_workflow.add_edge("chat_answer", END)

chat_graph = chat_workflow.compile()
