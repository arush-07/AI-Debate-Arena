from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
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
except ValueError as e:
    print(f"CRITICAL ERROR: {e}")
    debate_service = None
class DebateRequest(BaseModel):
    topic: str
    user_argument: str
    conversation_history: List[dict] = []

class AnalysisRequest(BaseModel):
    user_argument: str
@app.post("/api/v1/debate")
async def debate_turn(request: DebateRequest):
    if not debate_service:
        raise HTTPException(status_code=500, detail="API Key not configured in services.py")
    
    try:
        rebuttal = await debate_service.generate_rebuttal(
            request.topic, request.user_argument, request.conversation_history
        )
        return {"rebuttal": rebuttal}
    except Exception as e:
        print(f"❌ DEBATE ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_turn(request: AnalysisRequest):
    if not debate_service:
        raise HTTPException(status_code=500, detail="API Key not configured in services.py")

    try:
        return await debate_service.analyze_argument(request.user_argument)
    except Exception as e:
        print(f"❌ ANALYSIS ERROR: {e}")
        return AnalysisResponse(
            logic_score=50, 
            fallacies=[], 
            coaching_tip="System error during analysis. Keep debating!"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)