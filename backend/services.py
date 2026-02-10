import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_HERE"
class AnalysisResponse(BaseModel):
    logic_score: int = Field(..., description="Score 0-100 based on logical strength")
    fallacies: List[str] = Field(default_factory=list, description="List of logical fallacies found")
    coaching_tip: str = Field(..., description="Short, constructive tip for the user")

class DebateService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )

    async def generate_rebuttal(self, topic: str, argument: str, history: list) -> str:
       
        history_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in history[-5:]])

        template = """
        You are a world-class debater.
        Topic: {topic}
        Debate History: {history}
        Opponent's Argument: "{argument}"
        
        Goal: Dismantle the argument using logic. Keep it short (under 4 sentences).
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        response = await chain.ainvoke({
            "topic": topic,
            "history": history_text,
            "argument": argument
        })
        return response.content

    async def analyze_argument(self, argument: str) -> AnalysisResponse:
        
        structured_llm = self.llm.with_structured_output(AnalysisResponse)

        template = """
        Act as a neutral Debate Judge. Analyze the following argument strictly on logical merit.
        Argument: "{argument}"
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | structured_llm
        
        return await chain.ainvoke({"argument": argument})