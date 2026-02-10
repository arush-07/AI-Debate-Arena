from pydantic import BaseModel, Field
from typing import List, Optional
class DebateRequest(BaseModel):
    topic: str
    user_argument: str
    conversation_history: List[dict] = []
    model_name: str = "gemini-2.5-flash"  

class AnalysisRequest(BaseModel):
    user_argument: str
    topic: str
class OpponentResponse(BaseModel):
    rebuttal: str

class AnalysisResponse(BaseModel):
    logic_score: int = Field(..., description="Score 0-100")
    fallacies: List[str] = Field(default_factory=list)
    coaching_tip: str