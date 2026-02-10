import streamlit as st
import uuid
import pandas as pd
import plotly.express as px
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Debate Arena", page_icon="⚔️", layout="wide")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stProgress > div > div > div > div { background-color: #00FF41; }
    .ai-health > div > div > div > div { background-color: #FF4B4B; }
    .toast-popup { background-color: #333; color: white; }
</style>
""", unsafe_allow_html=True)

# --- API KEY SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "PASTE_YOUR_KEY_HERE"

# --- DATA MODELS ---
class TurnScore(BaseModel):
    user_logic: int = Field(..., description="0-100 score for user logic")
    user_relevance: int = Field(..., description="0-100 score for user relevance")
    ai_logic: int = Field(..., description="0-100 score for AI rebuttal strength")
    ai_relevance: int = Field(..., description="0-100 score for AI directness")
    winner: str = Field(..., description="'user' or 'ai' or 'draw'")
    reasoning: str = Field(..., description="Why this side won the turn")

class FinalAnalysis(BaseModel):
    winner: str = Field(..., description="Overall winner")
    best_point_user: str = Field(..., description="The user's strongest argument")
    weakest_point_user: str = Field(..., description="The user's weakest moment")
    improvement_tips: List[str] = Field(..., description="3 specific tips to improve")

# --- AI ENGINE ---
class DebateEngine:
    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                google_api_key=GOOGLE_API_KEY,
                temperature=0.7
            )
        except Exception as e:
            st.error(f"API Error: {e}")

    def generate_opening(self, topic: str, persona: str, stance: str):
        template = """
        You are debating as: {persona}. 
        Topic: "{topic}".
        Your Stance: You must ARGUE {stance} this topic.
        Generate a strong, 2-sentence opening argument.
        """
        try:
            prompt = ChatPromptTemplate.from_template(template)
            return self.llm.invoke(prompt.format_messages(topic=topic, persona=persona, stance=stance)).content
        except:
            return "Let's debate."

    def generate_rebuttal(self, topic: str, argument: str, history: list, persona: str, difficulty: str, stance: str):
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]])
        template = """
        Role: {role} ({difficulty})
        Topic: "{topic}"
        Stance: {stance}
        History: {history}
        User Argument: "{argument}"
        
        Rebut the user. Keep it under 4 sentences.
        """
        try:
            prompt = ChatPromptTemplate.from_template(template)
            return self.llm.invoke(prompt.format_messages(
                role=persona, difficulty=difficulty, topic=topic, 
                history=history_text, argument=argument, stance=stance
            )).content
        except:
            return "I disagree."

    def judge_turn(self, topic: str, user_arg: str, ai_arg: str):
        # Judges BOTH sides
        template = """
        Act as an Impartial Debate Judge.
        Topic: {topic}
        
        User Argument: "{user_arg}"
        AI Rebuttal: "{ai_arg}"
        
        Task:
        1. Score User's Logic & Relevance (0-100).
        2. Score AI's Logic & Relevance (0-100).
        3. Decide who won this specific exchange.
        4. Provide brief reasoning.
        """
        try:
            structured_llm = self.llm.with_structured_output(TurnScore)
            prompt = ChatPromptTemplate.from_template(template)
            return prompt | structured_llm | (lambda x: x.invoke({"topic": topic, "user_arg": user_arg, "ai_arg": ai_arg}))
        except:
            return TurnScore(user_logic=50, user_relevance=50, ai_logic=50, ai_relevance=50, winner="draw", reasoning="Error")

    def generate_final_report(self, history: list, topic: str):
        # Analyzes the whole match
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        template = """
        Analyze this full debate history.
        Topic: {topic}
        History: {history}
        
        Provide a detailed coaching report for the User.
        Identify their best point, worst point, and 3 tips.
        """
        try:
            structured_llm = self.llm.with_structured_output(FinalAnalysis)
            prompt = ChatPromptTemplate.from_template(template)
            return prompt | structured_llm | (lambda x: x.invoke({"history": history_text, "topic": topic}))
        except:
            return None

engine = DebateEngine()

# --- SESSION STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.user_hp = 100
    st.session_state.ai_hp = 100  # AI Health
    st.session_state.started = False
    st.session_state.turn_log = [] # Store scores for analysis
    
if "ai_side" not in st.session_state:
    st.session_state.ai_side = "AGAINST the Topic"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Arena Setup")
    topic = st.text_input("Topic:", "AI will replace doctors")
    col1, col2 = st.columns(2)
    with col1: persona = st.selectbox("Opponent:", ["Logical Vulcan", "Aggressive Troll", "Socratic Teacher"])
    with col2: difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard"])
    ai_side = st.radio("AI's Stance:", ["AGAINST", "IN FAVOUR"], index=0)
    
    if st.button("🔥 Start Debate", use_container_width=True):
        st.session_state.messages = []
        st.session_state.user_hp = 100
        st.session_state.ai_hp = 100
        st.session_state.started = True
        st.session_state.turn_log = []
        st.session_state.topic = topic
        st.session_state.persona = persona
        st.session_state.difficulty = difficulty
        st.session_state.ai_side = ai_side
        
        with st.spinner("AI Entering Arena..."):
            opening = engine.generate_opening(topic, persona, ai_side)
            st.session_state.messages.append({"role": "assistant", "content": opening})
        st.rerun()

    # --- LIVE SCOREBOARD ---
    if st.session_state.started:
        st.divider()
        st.subheader("🛡️ Live Health")
        
        # User HP
        st.write(f"**You:** {st.session_state.user_hp}/100")
        st.progress(st.session_state.user_hp / 100)
        
        # AI HP
        st.write(f"**Opponent ({persona}):** {st.session_state.ai_hp}/100")
        st.markdown(f"""
        <style>.stProgress .st-bo {{ background-color: red; }}</style>
        """, unsafe_allow_html=True)
        st.progress(st.session_state.ai_hp / 100)
        
        st.divider()
        if st.button("🏁 End & Analyze", type="primary", use_container_width=True):
            st.session_state.user_hp = 0 # Force end
            st.rerun()

# --- MAIN UI ---
st.title("⚔️ AI Debate Arena")

if not st.session_state.started:
    st.info("👈 Configure setup to begin.")
    st.stop()

# --- GAME OVER / ANALYSIS SCREEN ---
if st.session_state.user_hp <= 0 or st.session_state.ai_hp <= 0:
    winner = "YOU" if st.session_state.user_hp > 0 else "AI"
    if st.session_state.user_hp <= 0 and st.session_state.ai_hp <= 0: winner = "DRAW"
    
    st.header(f"🏁 DEBATE OVER! Winner: {winner}")
    
    with st.spinner("Generating Detailed Analysis..."):
        report = engine.generate_final_report(st.session_state.messages, st.session_state.topic)
        
        if report:
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"**Best Point:**\n{report.best_point_user}")
            with col2:
                st.error(f"**Weakest Point:**\n{report.weakest_point_user}")
            
            st.subheader("💡 Coaching Tips")
            for tip in report.improvement_tips:
                st.info(f"• {tip}")
    
    if st.button("Restart Debate"):
        st.session_state.started = False
        st.rerun()
    st.stop()

# --- CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- GAME LOOP ---
if prompt := st.chat_input("Your argument..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 1. Generate Rebuttal
            rebuttal = engine.generate_rebuttal(
                st.session_state.topic, prompt, st.session_state.messages, 
                st.session_state.persona, st.session_state.difficulty, st.session_state.ai_side
            )
            st.write(rebuttal)
            st.session_state.messages.append({"role": "assistant", "content": rebuttal})
            
            # 2. Judge Turn (Scores BOTH sides)
            score = engine.judge_turn(st.session_state.topic, prompt, rebuttal)
            
            # 3. Apply Damage
            user_dmg = 0
            ai_dmg = 0
            
            # User Penalty
            if score.user_relevance < 50: user_dmg += 20
            if score.user_logic < 50: user_dmg += 10
            if score.winner == "ai": user_dmg += 10
            
            # AI Penalty
            if score.ai_relevance < 50: ai_dmg += 20
            if score.ai_logic < 50: ai_dmg += 10
            if score.winner == "user": ai_dmg += 10 # Reward user for winning turn
            
            # Apply
            st.session_state.user_hp = max(0, st.session_state.user_hp - user_dmg)
            st.session_state.ai_hp = max(0, st.session_state.ai_hp - ai_dmg)
            
            # Notify
            if user_dmg > 0: st.toast(f"You took {user_dmg} DMG! ({score.reasoning})", icon="💥")
            if ai_dmg > 0: st.toast(f"AI took {ai_dmg} DMG! Good hit!", icon="🎯")
            
            # Update Session for Analysis
            st.session_state.turn_log.append(score)
            
            # Force UI Refresh for HP Bars
            time.sleep(0.5) 
            st.rerun()