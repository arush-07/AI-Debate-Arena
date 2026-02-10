import streamlit as st
import requests
import uuid
import time
st.set_page_config(page_title="AI Debate Arena", page_icon="⚔️", layout="wide")
API_URL = "http://localhost:8000/api/v1"
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #00FF41;
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .toast-popup {
        background-color: #333;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.user_hp = 100  
    st.session_state.round = 1
    st.session_state.game_over = False
    st.session_state.last_feedback = "Welcome to the Arena. State your case!"
   
    initial_topic = "Artificial General Intelligence (AGI) is a risk to humanity"
    st.session_state.topic = initial_topic
    st.session_state.messages.append({
        "role": "model", 
        "content": f"I argue that {initial_topic}. Prove me wrong."
    })


def reset_game():
    st.session_state.messages = []
    st.session_state.user_hp = 100
    st.session_state.round = 1
    st.session_state.game_over = False
    st.session_state.messages.append({
        "role": "model", 
        "content": f"I argue that {st.session_state.topic}. Prove me wrong."
    })
    st.rerun()
with st.sidebar:
    st.title("🛡️ Player Stats")
    hp = st.session_state.user_hp
    hp_color = "🟢" if hp > 70 else "🟡" if hp > 30 else "🔴"
    st.write(f"**Logic Integrity:** {hp}/100 {hp_color}")
    st.progress(hp / 100)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Round", st.session_state.round)
    with col2:
        status = "Alive" if not st.session_state.game_over else "Defeated"
        st.metric("Status", status)

    st.divider()
    st.markdown("### 🧠 Coach's Whisper")
    st.info(st.session_state.last_feedback)
    
    if st.button("🔄 New Debate", use_container_width=True):
        reset_game()


st.title("⚔️ AI Debate Arena")
st.caption(f"Topic: {st.session_state.topic}")


if st.session_state.user_hp <= 0:
    st.error("💀 GAME OVER. Your logic crumbled under pressure.")
    if st.button("Try Again?"):
        reset_game()
    st.stop()
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
if prompt := st.chat_input("Your argument..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)

    
    try:
        with st.spinner("⚖️ Judging logic..."):
            
            analyze_res = requests.post(
                f"{API_URL}/analyze",
                json={"user_argument": prompt} 
            )
            
            if analyze_res.status_code == 200:
                data = analyze_res.json()
                
               
                score = data.get("logic_score", 50)
                damage = 0
                
                if score < 50:
                    damage = (50 - score)
                    st.toast(f"💥 Weak Logic! Took {damage} damage!", icon="💥")
                    st.session_state.user_hp = max(0, st.session_state.user_hp - damage)
                elif score > 85:
                    heal = 10
                    st.toast(f"✨ Critical Point! Restored {heal} HP!", icon="✨")
                    st.session_state.user_hp = min(100, st.session_state.user_hp + heal)
                
                
                st.session_state.last_feedback = data.get("coaching_tip", "Keep going!")
                
                
                fallacies = data.get("fallacies", [])
                if fallacies:
                    for f in fallacies:
                        st.toast(f"🚩 Fallacy: {f}", icon="🚩")
                        st.session_state.user_hp -= 5 

    except Exception as e:
        st.error(f"Referee Error: {e}")


    if st.session_state.user_hp > 0:
        try:
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                full_response = ""
                
                with st.spinner("🤖 Formulating rebuttal..."):
                    debate_res = requests.post(
                        f"{API_URL}/debate",
                        json={
                            "topic": st.session_state.topic,
                            "user_argument": prompt,
                            "conversation_history": st.session_state.messages
                        }
                    )
                    
                    if debate_res.status_code == 200:
                        full_response = debate_res.json()["rebuttal"]
                        
                
                        for i in range(len(full_response)):
                            message_placeholder.markdown(full_response[:i+1] + "▌")
                            time.sleep(0.01) 
                        message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "model", "content": full_response})
            st.session_state.round += 1
            st.rerun()

        except Exception as e:
            st.error(f"Opponent Error: {e}")