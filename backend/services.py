import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

# --- PASTE YOUR API KEY HERE ---
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"

# --- Data Models ---
class AnalysisResponse(BaseModel):
    logic_score: int = Field(..., description="0-100 score for logical soundness")
    relevance_score: int = Field(..., description="0-100 score for staying on topic")
    evidence_score: int = Field(..., description="0-100 score for use of facts/examples")
    civility_score: int = Field(..., description="0-100 score for tone and politeness")
    conciseness_score: int = Field(..., description="0-100 score for brevity and clarity")
    fallacies: List[str] = Field(default_factory=list, description="List of logical fallacies found")
    coaching_tip: str = Field(..., description="Short, constructive tip for the user")
    fact_check: str = Field(..., description="A brief fact-check of the user's claims")

class DebateService:
    def __init__(self):
        # Initialize Gemini 1.5 Flash
        # We removed the specific safety import to prevent crashes
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )

    async def generate_opening(self, topic: str, persona: str) -> str:
        template = """
        You are debating as: {persona}. Topic: {topic}.
        Generate a strong, 2-sentence opening argument. Do NOT say "Prove me wrong."
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        # ✅ FIX: Direct Call (No Chains)
        messages = prompt.format_messages(topic=topic, persona=persona)
        response = await self.llm.ainvoke(messages)
        return response.content

    async def generate_rebuttal(self, topic: str, argument: str, history: list, persona: str, difficulty: str) -> str:
        # Safe history formatting
        history_text = ""
        if history:
            history_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in history[-5:]])
        
        persona_instructions = {
            "Logical Vulcan": "Purely logical, cold, focuses on data and contradictions.",
            "Aggressive Troll": "Emotional, interruptive, sarcastic. Try to flush the user.",
            "Socratic Teacher": "Ask probing questions to make the user realize their own errors.",
            "Devil's Advocate": "Contrarian but polite. Always find the opposing view.",
            "The Bureaucrat": "Obsessed with definitions and citations. Demand proof for everything."
        }
        
        difficulty_prompts = {
            "Easy": "Use simple language. Make occasional logical errors.",
            "Medium": "Standard debate level. Competent and clear.",
            "Hard": "Use complex vocabulary. Be ruthless about weak points.",
            "God Mode": "You are omniscient. Point out every micro-contradiction. You never lose."
        }
        
        role_inst = persona_instructions.get(persona, "Skilled debater.")
        diff_inst = difficulty_prompts.get(difficulty, "Standard level.")

        template = """
        Role: {role_inst}
        Difficulty Level: {diff_inst}
        Topic: {topic}
        History: {history}
        User Argument: "{argument}"
        
        Respond to the user based on your Role and Difficulty. Keep it under 4 sentences.
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        # ✅ FIX: Direct Call (No Chains)
        messages = prompt.format_messages(
            role_inst=role_inst, 
            diff_inst=diff_inst, 
            topic=topic, 
            history=history_text, 
            argument=argument
        )
        response = await self.llm.ainvoke(messages)
        return response.content

    async def analyze_argument(self, argument: str, topic: str) -> AnalysisResponse:
        structured_llm = self.llm.with_structured_output(AnalysisResponse)

        template = """
        Act as a neutral Debate Judge.
        Topic: {topic}
        Argument: "{argument}"
        
        Provide scores (0-100) for:
        1. Logic
        2. Relevance
        3. Evidence
        4. Civility
        5. Conciseness
        
        Also identify fallacies, check facts, and give a tip.
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        # ✅ FIX: Direct Call
        chain = prompt | structured_llm
        return await chain.ainvoke({"argument": argument, "topic": topic})