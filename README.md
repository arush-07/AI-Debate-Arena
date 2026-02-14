# ⚔️ AI Debate Arena
<div align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI-Gemini%202.5-orange?style=for-the-badge&logo=google" alt="Gemini">
</div>

<br />
A **Next-Gen Gamified Debate Simulator** built using **Streamlit + Google Gemini 2.5 Flash + LangChain**, designed to make critical thinking interactive, competitive, and multilingual.

---

## 🚀 About

**AI Debate Arena** transforms traditional debates into a **real-time gamified experience** where users battle AI opponents using logic and reasoning.

The system leverages **Google Gemini 2.5 Flash** with **LangChain orchestration** to:
- Generate arguments & rebuttals
- Judge debates impartially
- Provide structured feedback
- Support multilingual debates 🎙️

With features like **health points (HP), AI personas, voice input, and post-match analysis**, it simulates a **high-stakes debate battlefield**.

---

## 🎯 Key Features

### ⚔️ Gamified Debate System
- Health Points (HP) for both user and AI
- Logical superiority = damage to opponent
- Real-time feedback with crowd reactions

### 🤖 Adaptive AI Personas
Debate against unique personalities:
- 🧠 Logical Vulcan  
- 😏 Sarcastic Troll  
- 📚 Philosopher  
- 😈 Devil’s Advocate  

### ⚖️ AI Judge System
- Scores each turn based on:
  - Logic
  - Reasoning
- Detects logical fallacies
- Decides winner per round

### 🗣️ Multilingual Support
Debate in multiple languages:
- English, Hindi, Gujarati, Marathi, Tamil, Telugu, Kannada, Punjabi

### 🎤 Voice Input + AI Voice Output
- Speak your arguments (speech-to-text via Gemini)
- Listen to AI responses (text-to-speech using gTTS)

### 📊 Post-Debate Analysis
- Best argument 💎
- Weakest argument 📉
- Personalized improvement tips 💡

### 🎬 AI vs AI Simulation Mode
- Watch two AI personas debate autonomously
- Great for learning argument styles

### 📜 Downloadable Debate Logs
- Export full debate history as `.txt`

---

## 🧠 Technology Stack

| Component | Technology |
|----------|-----------|
| **Frontend** | Streamlit |
| **Backend Logic** | Python |
| **LLM / AI** | Google Gemini 2.5 Flash |
| **Orchestration** | LangChain |
| **Validation** | Pydantic |
| **Speech** | gTTS (Text-to-Speech) |
| **Audio Processing** | Gemini API |

---

## 📁 Project Structure
AI-DEBATE-ARENA/
├── streamlit_app.py # Main application (UI + AI logic)
├── requirements.txt # Dependencies
└── README.md # Project documentation
