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
    .toast-popup { background-color: #333; color: white; }
</style>
""", unsafe_allow_html=True)

# --- API KEY SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "PASTE_YOUR_KEY_HERE"

# --- DATA MODELS ---
class AnalysisResponse(BaseModel):
    logic_score: int = Field(..., description="0-100 score for logic")
    relevance_score: int = Field(..., description="0-100 score for relevance")
    evidence_score: int = Field(..., description="0-100 score for evidence")
    civility_score: int = Field(..., description="0-100 score for civility")
    conciseness_score: int = Field(..., description="0-100 score for brevity")
    fallacies: List[str] = Field(default_factory=list, description="List of logical fallacies")
    coaching_tip: str = Field(..., description="Short coaching tip")

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
        
        Generate a strong, 2-sentence opening argument reflecting this stance.
        """
        prompt = ChatPromptTemplate.from_template(template)
        try:
            messages = prompt.format_messages(topic=topic, persona=persona, stance=stance)
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error: {e}"

    def generate_rebuttal(self, topic: str, argument: str, history: list, persona: str, difficulty: str, stance: str):
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]])
        
        persona_map = {
            "Logical Vulcan": "Purely logical, cold, data-driven.",
            "Aggressive Troll": "Emotional, sarcastic, interruptive.",
            "Socratic Teacher": "Asks deep probing questions.",
            "Devil's Advocate": "Contrarian but polite.",
            "The Bureaucrat": "Obsessed with definitions and citations."
        }
        
        template = """
        Role: {role}
        Difficulty: {difficulty}
        Topic: "{topic}"
        YOUR FIXED STANCE: You are arguing {stance} the topic. Never switch sides.
        
        Debate History:
        {history}
        
        Opponent's Latest Argument: "{argument}"
        
        Task: Rebut the opponent while strictly maintaining your stance ({stance}). Keep it under 4 sentences.
        """
        prompt = ChatPromptTemplate.from_template(template)
        try:
            messages = prompt.format_messages(
                role=persona_map.get(persona, "Debater"),
                difficulty=difficulty,
                topic=topic,
                history=history_text,
                argument=argument,
                stance=stance
            )
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error: {e}"

    def analyze_argument(self, argument: str, topic: str):
        try:
            structured_llm = self.llm.with_structured_output(AnalysisResponse)
            template = """
            Act as a Debate Judge. Topic: {topic}. Argument: "{argument}".
            Score (0-100): Logic, Relevance, Evidence, Civility, Conciseness.
            Identify fallacies and give a tip.
            """
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | structured_llm
            return chain.invoke({"argument": argument, "topic": topic})
        except:
            return AnalysisResponse(
                logic_score=50, relevance_score=50, evidence_score=50, 
                civility_score=50, conciseness_score=50, 
                fallacies=[], coaching_tip="Analysis unavailable."
            )

# Initialize Engine
engine = DebateEngine()

# --- BULLETPROOF SESSION STATE INITIALIZATION ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.user_hp = 100
    st.session_state.started = False
    st.session_state.radar_data = {"Logic": 50, "Relevance": 50, "Evidence": 50, "Civility": 50, "Conciseness": 50}

# ✅ FIX: Separate check for ai_side so it catches old sessions too
if "ai_side" not in st.session_state:
    st.session_state.ai_side = "AGAINST the Topic"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Debate Settings")
    
    # 1. Topic
    topic = st.text_input("Topic:", "AI will replace doctors")

    # 2. Settings
    col1, col2 = st.columns(2)
    with col1:
        persona = st.selectbox("Opponent:", ["Logical Vulcan", "Aggressive Troll", "Socratic Teacher", "Devil's Advocate", "The Bureaucrat"])
    with col2:
        difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard", "God Mode"])
    
    # 3. AI Stance Selector
    ai_side = st.radio("AI's Position:", ["AGAINST the Topic", "IN FAVOUR of the Topic"], index=0)

    st.divider()

    if st.button("🔥 Start Debate", use_container_width=True):
        st.session_state.messages = []
        st.session_state.user_hp = 100
        st.session_state.started = True
        st.session_state.topic = topic
        st.session_state.persona = persona
        st.session_state.difficulty = difficulty
        st.session_state.ai_side = ai_side # Update state with user choice
        
        with st.spinner(f"AI is preparing to argue {ai_side}..."):
            opening = engine.generate_opening(topic, persona, ai_side)
            st.session_state.messages.append({"role": "assistant", "content": opening})
        st.rerun()

    # Radar Chart Display
    if st.session_state.started:
        st.subheader("📊 Skill Analysis")
        df = pd.DataFrame(dict(
            r=list(st.session_state.radar_data.values()),
            theta=list(st.session_state.radar_data.keys())
        ))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,100])
        fig.update_traces(fill='toself', line_color='#00FF41')
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )
        st.plotly_chart(fig, use_container_width=True)

# --- MAIN UI ---
st.title("⚔️ AI Debate Arena")

if not st.session_state.started:
    st.info("👈 Set the Topic and AI's Position, then click Start.")
    st.stop()

if st.session_state.user_hp <= 0:
    st.error("💀 GAME OVER")
    if st.button("Restart"):
        st.session_state.started = False
        st.rerun()
    st.stop()

# Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input
if prompt := st.chat_input("Your argument..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    # 1. Analyze
    with st.spinner("Judging..."):
        analysis = engine.analyze_argument(prompt, st.session_state.topic)
        
        # Update Radar
        st.session_state.radar_data = {
            "Logic": analysis.logic_score, "Relevance": analysis.relevance_score,
            "Evidence": analysis.evidence_score, "Civility": analysis.civility_score,
            "Conciseness": analysis.conciseness_score
        }
        
        # Damage Logic
        damage = 0
        if analysis.relevance_score < 50: 
            damage += 15
            st.toast("🚫 Off-Topic!", icon="🚫")
        if analysis.logic_score < 50: 
            damage += 10
            st.toast("📉 Weak Logic", icon="📉")
        
        if damage > 0:
            st.session_state.user_hp = max(0, st.session_state.user_hp - damage)

    # 2. Rebuttal
    if st.session_state.user_hp > 0:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                rebuttal = engine.generate_rebuttal(
                    st.session_state.topic, 
                    prompt, 
                    st.session_state.messages, 
                    st.session_state.persona, 
                    st.session_state.difficulty,
                    st.session_state.ai_side  # Safe call
                )
                st.write(rebuttal)
                st.session_state.messages.append({"role": "assistant", "content": rebuttal})
                st.rerun()