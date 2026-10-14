from pydantic import BaseModel, Field
from typing import List, Optional

class UserPreferences(BaseModel):
    location_tracking: str = "Ask Me"
    personalized_ads: str = "Ask Me"
    third_party_sharing: str = "Ask Me"
    data_retention: str = "Ask Me"
    sensitive_data: str = "Ask Me"

# The data we expect to RECEIVE from the extension
class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="The URL of the webpage")
    title: str = Field(..., description="The title of the webpage")
    text: str = Field(..., max_length=150000, description="The extracted text from the webpage")
    preferences: Optional[UserPreferences] = Field(None, description="The user's privacy preferences")

class Clause(BaseModel):
    name: str = Field(..., description="Short name of the clause, e.g., 'Data Sharing'")
    description: str = Field(..., description="Explanation of what this clause means")
    risk_level: str = Field(..., description="Risk level (Low, Medium, High, Critical)")
    evidence: str = Field(..., description="Direct quote from the text that proves this")

# ---------------------------------------------------------
# Intermediate Agent Output Models
# ---------------------------------------------------------

# Agent 1 Output
class ExtractedClauses(BaseModel):
    important_clauses: List[Clause] = Field(..., description="List of important privacy clauses found")

# Agent 1.5 Output (RAG)
class ComplianceOutput(BaseModel):
    compliance_notes: str = Field(..., description="Cautious compliance notes based on retrieved legal text")

# Agent 2 Output
class RiskAnalysis(BaseModel):
    summary: str = Field(..., description="Simple overall summary based on the clauses")
    risk_score: float = Field(..., description="Number from 1.0 to 10.0")
    risk_level: str = Field(..., description="Overall risk level (Low, Medium, High, Critical)")

# Agent 3 Output
class RecommendationOutput(BaseModel):
    recommendation: str = Field(..., description="Basic recommendation for the user")
    explanation: str = Field(..., description="A short explanation justifying the recommendation")

# Agent 4 Output (Comparison)
class ClauseChange(BaseModel):
    type: str = Field(..., description="'ADDED', 'REMOVED', or 'CHANGED'")
    description: str = Field(..., description="Description of what changed")

class ComparisonResult(BaseModel):
    changes: List[ClauseChange] = Field(..., description="List of changes between old and new policy")
    increased_risks: List[str] = Field(..., description="Any newly increased risks")
    new_concerns: List[str] = Field(..., description="Any newly introduced privacy concerns")

# ---------------------------------------------------------
# Final Combined Output
# ---------------------------------------------------------

class AnalysisResult(BaseModel):
    summary: str = Field(..., description="Simple overall summary")
    risk_score: float = Field(..., description="Number from 1.0 to 10.0")
    risk_level: str = Field(..., description="Overall risk level (Low, Medium, High, Critical)")
    important_clauses: List[Clause] = Field(..., description="List of important privacy clauses found")
    compliance_notes: str = Field(default="No compliance issues detected.", description="Cautious compliance notes from RAG")
    recommendation: str = Field(..., description="Basic recommendation for the user")
    explanation: str = Field(..., description="A short explanation justifying the recommendation")
    comparison: Optional[ComparisonResult] = Field(None, description="Results of comparing with an older version")

# ---------------------------------------------------------
# Chat Models
# ---------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="The message content")

class ChatRequest(BaseModel):
    query: str = Field(..., description="The current user question")
    messages: List[ChatMessage] = Field(..., description="Previous chat messages")
    policy_text: str = Field(..., description="The raw policy text")
    analysis: AnalysisResult = Field(..., description="The structured analysis result")
    preferences: Optional[UserPreferences] = Field(None, description="User's privacy preferences")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI's answer")
