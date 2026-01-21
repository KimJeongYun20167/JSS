import streamlit as st
from groq import Groq
#Page config
st.set_page_config(page_title="JSS", page_icon="📚", layout="wide")

#Groq 불러오기
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY가 Secrets에 없어!!!!!!")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

#사이드바(프로필 넣을 거)
st.sidebar.title("System Mode")

mode = st.sidebar.selectbox(
    "Choose mode",
    ["Basic Support Mode", "Advanced Support Mode"],
    index=0,
)

st.sidebar.subheader("Student profile")
goal = st.sidebar.text_input("Goal (e.g., raise math score to 80)", "")
daily_time = st.sidebar.selectbox("Daily study time", ["10–20 min", "20–40 min", "40–60 min", "60+ min"], index=0)
level = st.sidebar.selectbox("Self-reported level", ["Beginner", "Intermediate", "Advanced"], index=0)

if st.sidebar.button("Reset chat"):
    st.session_state.messages = []
    st.rerun()

# -----------------------------
#시스템
def build_system_prompt(mode: str, goal: str, daily_time: str, level: str) -> str:
    if mode.startswith("Basic Support Mode"):
        return f"""
You are JSS, a friendly AI study advisor for basic support mode settings.
Rules:
- Use very simple English (CEFR A2–B1).
- Keep answers short: 3–6 sentences.
- Prefer step-by-step plans and quick checks.
- Avoid jargon and long paragraphs.
Context:
- Student level: {level}
- Daily study time: {daily_time}
- Goal: {goal if goal else "not specified"}
Task:
Give practical study help and encouragement.
"""
    else:
        return f"""
You are JSS, a warm, personalized AI study advisor.
Rules:
- Be supportive and specific.
- Ask 1 short follow-up question if needed.
- Provide a clear plan (bullets) + a quick next step.
Context:
- Student level: {level}
- Daily study time: {daily_time}
- Goal: {goal if goal else "not specified"}
Task:
Coach the student like a real study counselor: diagnose issue, propose plan, motivate.
"""

#채팅 ui
st.title("JSS")
st.caption("A level-based study counseling chatbot.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’m JSS. Tell me what you’re struggling with, and I’ll help you."}
    ]

# show chat history
for m in st.session_state.messages:
    with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
        st.write(m["content"])

# user input
user_text = st.chat_input("Type your message...")

def groq_chat(system_prompt: str, history: list[dict], user_text: str) -> str:
    # Groq messages format: system + history + new user msg
    msgs = [{"role": "system", "content": system_prompt}]
    for m in history:
        # keep only user/assistant roles
        if m["role"] in ("user", "assistant"):
            msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": user_text})
##################################
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=msgs,
        temperature=0.7,
        max_tokens=400,
    )
    return completion.choices[0].message.content

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    system_prompt = build_system_prompt(mode, goal, daily_time, level)

    try:
        reply = groq_chat(system_prompt, st.session_state.messages[:-1], user_text)
    except Exception as e:
        st.error(f"Groq 호출 중 오류: {e}")
        st.stop()

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
