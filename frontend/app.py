import streamlit as st
import requests
import uuid
import time
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Debate Arena", page_icon="⚔️", layout="wide")
API_URL = "http://localhost:8000/api/v1"

# --- CSS ---
st.markdown("""
<style>
    .stProgress > div > div > div > div { background-color: #00FF41; }
</style>
""", unsafe_allow_html=True)

# --- INIT STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.user_hp = 100
    st.session_state.round = 1
    st.session_state.game_over = False
    st.session_state.last_feedback = "Welcome. Configure settings to start."
    st.session_state.started = False
    # Init Radar Data
    st.session_state.radar_data = {
        "Logic": 50, "Relevance": 50, "Evidence": 50, "Civility": 50, "Conciseness": 50
    }

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Dojo Settings")
    
    # 1. Configuration
    persona = st.selectbox("Opponent Persona:", 
        ["Logical Vulcan", "Aggressive Troll", "Socratic Teacher", "Devil's Advocate", "The Bureaucrat"])
    
    difficulty = st.selectbox("Difficulty Level:", 
        ["Easy", "Medium", "Hard", "God Mode"])
        
    topic_input = st.text_input("Topic:", "AI will replace doctors")
    
    # 2. Start Button
    if st.button("🔥 Enter Arena", use_container_width=True):
        st.session_state.messages = []
        st.session_state.user_hp = 100
        st.session_state.round = 1
        st.session_state.game_over = False
        st.session_state.topic = topic_input
        st.session_state.persona = persona
        st.session_state.difficulty = difficulty
        st.session_state.started = True
        
        # Get Opening
        with st.spinner("Opponent is preparing..."):
            try:
                res = requests.post(f"{API_URL}/opening", json={"topic": topic_input, "persona": persona})
                intro_msg = res.json()["opening"] if res.status_code == 200 else "Let's debate."
            except:
                intro_msg = "Let's debate."
        st.session_state.messages.append({"role": "model", "content": intro_msg})
        st.rerun()

    # 3. Stats & Charts
    if st.session_state.started:
        st.divider()
        st.metric("HP", f"{st.session_state.user_hp}/100")
        st.progress(st.session_state.user_hp / 100)
        
        # RADAR CHART VISUALIZATION
        st.subheader("📊 Skill Analysis")
        df = pd.DataFrame(dict(
            r=[st.session_state.radar_data[k] for k in st.session_state.radar_data],
            theta=list(st.session_state.radar_data.keys())
        ))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,100])
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        fig.update_traces(fill='toself', line_color='#00FF41')
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"Coach: {st.session_state.last_feedback}")

# --- MAIN UI ---
st.title("⚔️ AI Debate Arena")

if not st.session_state.started:
    st.info("👈 Configure your opponent and difficulty to begin.")
    st.stop()

if st.session_state.user_hp <= 0:
    st.error("💀 GAME OVER.")
    if st.button("Restart"):
        st.session_state.started = False
        st.rerun()
    st.stop()

# Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
        st.write(msg["content"])

# --- GAME LOOP ---
if prompt := st.chat_input("Your argument..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): st.write(prompt)

    # ANALYSIS
    try:
        with st.spinner("Analyzing Skills..."):
            res = requests.post(f"{API_URL}/analyze", json={"user_argument": prompt, "topic": st.session_state.topic})
            if res.status_code == 200:
                data = res.json()
                
                # Update Radar Data
                st.session_state.radar_data = {
                    "Logic": data["logic_score"],
                    "Relevance": data["relevance_score"],
                    "Evidence": data["evidence_score"],
                    "Civility": data["civility_score"],
                    "Conciseness": data["conciseness_score"]
                }
                
                st.session_state.last_feedback = data.get("coaching_tip", "")
                
                # Damage Logic (Based on Logic & Relevance)
                damage = 0
                if data["relevance_score"] < 50:
                    damage += 20
                    st.toast("🚫 Off-Topic!", icon="🚫")
                if data["logic_score"] < 50:
                    damage += 10
                    st.toast("📉 Weak Logic", icon="📉")
                if data["civility_score"] < 40:
                    damage += 10
                    st.toast("🤬 Rude!", icon="🤬")

                st.session_state.user_hp = max(0, st.session_state.user_hp - damage)
    except:
        st.error("Analysis Failed")

    # OPPONENT REBUTTAL
    if st.session_state.user_hp > 0:
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            res = requests.post(f"{API_URL}/debate", json={
                "topic": st.session_state.topic, 
                "user_argument": prompt, 
                "conversation_history": st.session_state.messages, 
                "persona": st.session_state.persona,
                "difficulty": st.session_state.difficulty
            })
            if res.status_code == 200:
                reply = res.json()["rebuttal"]
                placeholder.markdown(reply)
                st.session_state.messages.append({"role": "model", "content": reply})
                st.rerun() # Refresh to update chart