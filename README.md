# ⚔️ AI Debate Arena
<div align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI-Gemini%202.5-orange?style=for-the-badge&logo=google" alt="Gemini">
</div>

<br />

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
##  Repo Structure
```
bash
AI-DEBATE-ARENA/
├── streamlit_app.py    # Main application logic (Frontend + AI Backend)
├── requirements.txt    # List of project dependencies
└── README.md           # Project documentation
```
## How to Clone
```
bash
git clone https://github.com/arush-07/AI-DEBATE-ARENA.git
cd AI-DEBATE-ARENA
```

---

## Install Dependencies

Make sure you have *Python 3.9+* installed.
```
bash
pip install -r requirements.txt
```

---

## Set Up Environment Variables

You need a *Google Gemini API Key*.

### Option 1: Set as Environment Variable (Recommended)

*Windows (PowerShell):*
```
powershell
setx GOOGLE_API_KEY "your_api_key_here"

```
*Mac/Linux:*
bash
export GOOGLE_API_KEY="your_api_key_here"
```

### Option 2: Create a .env File

Create a .env file in the root directory:

```
GOOGLE_API_KEY=your_api_key_here


---

## Run the Application
```
bash
streamlit run streamlit_app.py
```

Your app will open automatically in your browser 

##  Team Bitwise
Made by:

- *Arush Pradhan*
- *Drishti Verma*
- *Aarav Parikh*

<div align="center">
  <i>Built for the IIIT Surat hackathon.</i>
</div>
