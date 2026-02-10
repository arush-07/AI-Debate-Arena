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
# This looks for the key in Streamlit Secrets (Cloud) or uses a fallback
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("🚨 API Key missing! Please set GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

# --- DATA MODELS ---
class AnalysisResponse(BaseModel):
    logic_score: int = Field(..., description="0-100 score for logic")
    relevance_score: int = Field(..., description="0-100 score for relevance")
    evidence_score: int = Field(..., description="0-100 score for evidence")
    civility_score: int = Field(..., description="0-100 score for civility")
    conciseness_score: int = Field(..., description="0-100 score for brevity")
    fallacies: List[str] = Field(default_factory=list, description="List of logical fallacies")
    coaching_tip: str = Field(..., description="Short coaching tip")

# --- AI ENGINE (Merged from Backend) ---
class DebateEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )

    def generate_opening(self, topic: str, persona: str):
        template = "You are debating as: {persona}. Topic: {topic}. Generate a strong, 2-sentence opening argument. Do NOT say 'Prove me wrong.'"
        prompt = ChatPromptTemplate.from_template(template)
        # Direct invoke
        messages = prompt.format_messages(topic=topic, persona=persona)
        response = self.llm.invoke(messages)
        return response.content

    def generate_rebuttal(self, topic: str, argument: str, history: list, persona: str, difficulty: str):
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
        Topic: {topic}
        History: {history}
        Opponent Argument: "{argument}"
        
        Respond under 4 sentences.
        """
        prompt = ChatPromptTemplate.from_template(template)
        messages = prompt.format_messages(
            role=persona_map.get(persona, "Debater"),
            difficulty=difficulty,
            topic=topic,
            history=history_text,
            argument=argument
        )
        response = self.llm.invoke(messages)
        return response.content

    def analyze_argument(self, argument: str, topic: str):
        structured_llm = self.llm.with_structured_output(AnalysisResponse)
        template = """
        Act as a Debate Judge. Topic: {topic}. Argument: "{argument}".
        Score (0-100): Logic, Relevance, Evidence, Civility, Conciseness.
        Identify fallacies and give a tip.
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | structured_llm
        return chain.invoke({"argument": argument, "topic": topic})

# Initialize Engine
engine = DebateEngine()

# --- SESSION STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.user_hp = 100
    st.session_state.started = False
    st.session_state.radar_data = {"Logic": 50, "Relevance": 50, "Evidence": 50, "Civility": 50, "Conciseness": 50}
    st.session_state.last_feedback = "Ready to start?"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Dojo Settings")
    persona = st.selectbox("Opponent:", ["Logical Vulcan", "Aggressive Troll", "Socratic Teacher", "Devil's Advocate", "The Bureaucrat"])
    difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard", "God Mode"])
    topic = st.text_input("Topic:", "AI will replace doctors")
    
    if st.button("🔥 Start Debate", use_container_width=True):
        st.session_state.messages = []
        st.session_state.user_hp = 100
        st.session_state.started = True
        st.session_state.topic = topic
        st.session_state.persona = persona
        st.session_state.difficulty = difficulty
        
        with st.spinner("Opponent is preparing..."):
            opening = engine.generate_opening(topic, persona)
            st.session_state.messages.append({"role": "assistant", "content": opening})
        st.rerun()

    if st.session_state.started:
        st.divider()
        st.metric("HP", f"{st.session_state.user_hp}/100")
        st.progress(st.session_state.user_hp / 100)
        
        # Radar Chart
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
    st.info("👈 Configure the debate in the sidebar and click Start.")
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
        try:
            analysis = engine.analyze_argument(prompt, st.session_state.topic)
            st.session_state.radar_data = {
                "Logic": analysis.logic_score, "Relevance": analysis.relevance_score,
                "Evidence": analysis.evidence_score, "Civility": analysis.civility_score,
                "Conciseness": analysis.conciseness_score
            }
            
            # HP Damage Logic
            damage = 0
            if analysis.relevance_score < 50: 
                damage += 15
                st.toast("🚫 Off-Topic!", icon="🚫")
            if analysis.logic_score < 50: 
                damage += 10
                st.toast("📉 Weak Logic", icon="📉")
            
            if damage > 0:
                st.session_state.user_hp = max(0, st.session_state.user_hp - damage)
        except Exception as e:
            st.error(f"Analysis Error: {e}")

    # 2. Rebuttal
    if st.session_state.user_hp > 0:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                rebuttal = engine.generate_rebuttal(
                    st.session_state.topic, prompt, st.session_state.messages, 
                    st.session_state.persona, st.session_state.difficulty
                )
                st.write(rebuttal)
                st.session_state.messages.append({"role": "assistant", "content": rebuttal})
                st.rerun()