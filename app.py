import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="JSS Study Advisor", page_icon="📚")
st.title("📚 JSS: AI Study Advisor")

# --- Mode ---
mode = st.sidebar.selectbox(
    "System Mode (by digital infrastructure)",
    ["Low-infrastructure (Voice/Simple)", "High-infrastructure (Personalized)"]
)

# --- Simple personalization profile ---
st.sidebar.markdown("### Student profile")
goal = st.sidebar.text_input("Goal (e.g., raise math score to 80)", "")
study_time = st.sidebar.selectbox("Daily study time", ["10–20 min", "30–60 min", "1–2 hours", "2+ hours"])
level = st.sidebar.selectbox("Self-reported level", ["Beginner", "Intermediate", "Advanced"])

if st.sidebar.button("Reset chat"):
    st.session_state.clear()
    st.rerun()

# --- OpenAI client ---
from openai import OpenAI
import streamlit as st

api_key = st.secrets["OPENAI_API_KEY"].strip()  # <- 핵심: strip()
client = OpenAI(api_key=api_key)

# --- System prompt (tone + rules) ---
def build_system_prompt(mode: str, goal: str, study_time: str, level: str) -> str:
    base = f"""
You are JSS, an AI study advisor and learning coach.
You provide academic guidance and emotional support.
You MUST be warm, encouraging, and practical (not robotic).
You ask 1–2 short clarifying questions when needed.
You give a simple step-by-step plan and next action.

Student profile:
- Goal: {goal if goal else "unknown"}
- Daily study time: {study_time}
- Level: {level}

Safety:
- Do not give medical/legal advice.
- If the user shows severe distress or self-harm intent, encourage seeking help from a trusted adult or professional.
"""

    if "Low-infrastructure" in mode:
        base += """
Mode: Low-infrastructure.
- Use very simple English.
- Keep replies short (2–5 sentences).
- Offer choices like (A/B) or Yes/No.
- Assume limited reading ability and unstable internet.
"""
    else:
        base += """
Mode: High-infrastructure.
- Give more detailed personalization.
- Suggest a weekly plan if asked.
- Use friendly but professional tone.
"""
    return base.strip()

# --- Message state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’m JSS 😊 What are you studying today, and what’s the biggest challenge right now?"}
    ]

# --- Render chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input ---
user_text = st.chat_input("Type your message...")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    system_prompt = build_system_prompt(mode, goal, study_time, level)

    # Build messages for API (system + history)
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages += st.session_state.messages[-12:]  # last 12 turns for context

    with st.chat_message("assistant"):
        with st.spinner("JSS is thinking..."):
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=api_messages,
                temperature=0.7
            )
            reply = resp.choices[0].message.content

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
