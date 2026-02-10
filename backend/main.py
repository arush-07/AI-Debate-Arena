from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import traceback  # <--- NEW: Helps us see the error
from services import DebateService, AnalysisResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    debate_service = DebateService()
except Exception as e:
    print("❌ CRITICAL ERROR INITIALIZING SERVICE:")
    traceback.print_exc() # Print full error to terminal
    debate_service = None

# --- Models ---
class DebateRequest(BaseModel):
    topic: str
    user_argument: str
    conversation_history: List[dict] = []
    persona: str = "Logical Vulcan"
    difficulty: str = "Medium"

class OpeningRequest(BaseModel):
    topic: str
    persona: str

class AnalysisRequest(BaseModel):
    user_argument: str
    topic: str

# --- Endpoints ---
@app.post("/api/v1/opening")
async def get_opening(request: OpeningRequest):
    if not debate_service: 
        raise HTTPException(status_code=500, detail="Service not initialized")
    try:
        opening = await debate_service.generate_opening(request.topic, request.persona)
        return {"opening": opening}
    except Exception as e:
        print(f"❌ ERROR IN OPENING:")
        traceback.print_exc()  # <--- THIS WILL PRINT THE REAL ERROR
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/debate")
async def debate_turn(request: DebateRequest):
    try:
        rebuttal = await debate_service.generate_rebuttal(
            request.topic, request.user_argument, request.conversation_history, 
            request.persona, request.difficulty
        )
        return {"rebuttal": rebuttal}
    except Exception as e:
        print(f"❌ ERROR IN DEBATE:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_turn(request: AnalysisRequest):
    try:
        return await debate_service.analyze_argument(request.user_argument, request.topic)
    except Exception as e:
        print(f"❌ ERROR IN ANALYZE:")
        traceback.print_exc()
        return AnalysisResponse(
            logic_score=50, relevance_score=50, evidence_score=50, civility_score=50, conciseness_score=50,
            fallacies=[], coaching_tip="System Error", fact_check="N/A"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)