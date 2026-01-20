import streamlit as st
from openai import OpenAI

# -------------------------
# 0) Page config
# -------------------------
st.set_page_config(page_title="JSS: AI Study Advisor", page_icon="📚", layout="wide")

# -------------------------
# 1) OpenAI client
# -------------------------
# Streamlit Secrets에 OPENAI_API_KEY가 있어야 함
# 예) OPENAI_API_KEY = "sk-..."
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
api_key = st.secrets["OPENAI_API_KEY"]

st.sidebar.write("Key startswith 'sk-':", api_key.startswith("sk-"))
st.sidebar.write("Key length:", len(api_key))
st.sidebar.write("Key is ASCII:", api_key.isascii())

# non-ascii 문자 개수만 표시 (내용은 안 보여줌)
bad = [c for c in api_key if not c.isascii()]
st.sidebar.write("Non-ASCII char count:", len(bad))
# -------------------------
# 2) Helpers
# -------------------------
def build_system_prompt(mode: str, profile: dict) -> str:
    """
    mode:
      - "Low-infrastructure (Voice/Simple)"
      - "High-infrastructure (Personalized)"
    profile:
      - goal, daily_time, level
    """
    base = """
You are JSS, a friendly AI study advisor and learning coach.
Your job:
- Give practical study advice in a warm, supportive tone.
- Ask 1 short follow-up question when needed.
- Provide a simple plan (steps) instead of long theory.
- Keep answers concise (about 4–8 short sentences).
- If the user seems stressed, add 1 sentence of emotional support.
"""
    # 모드별로 “가능한 기능 수준”을 다르게
    if "Low-infrastructure" in mode:
        mode_rules = """
System constraints (LOW infrastructure):
- Assume the student may have limited internet/devices.
- Prefer simple, low-data solutions: short routines, offline practice, paper-based methods.
- Offer voice-friendly guidance: very clear steps, minimal jargon.
- If the student asks for advanced analytics, explain a simpler alternative.
"""
    else:
        mode_rules = """
System constraints (HIGH infrastructure):
- Assume stable internet/devices available.
- Provide more personalized guidance using the student's goal/time/level.
- Suggest adaptive practice, tracking, spaced repetition, and targeted drills.
- You may propose a weekly plan and progress tracking.
"""

    goal = profile.get("goal", "").strip()
    daily_time = profile.get("daily_time", "").strip()
    level = profile.get("level", "").strip()

    profile_block = f"""
Student profile:
- Goal: {goal if goal else "Not provided"}
- Daily study time: {daily_time if daily_time else "Not provided"}
- Self-reported level: {level if level else "Not provided"}
"""

    return base + mode_rules + profile_block


def ensure_session_state():
    if "chat" not in st.session_state:
        st.session_state.chat = []  # list of {"role": "...", "content": "..."}
    if "mode" not in st.session_state:
        st.session_state.mode = "Low-infrastructure (Voice/Simple)"
    if "profile" not in st.session_state:
        st.session_state.profile = {"goal": "", "daily_time": "10–20 min", "level": "Beginner"}


def render_chat():
    # 간단한 말풍선 UI
    for msg in st.session_state.chat:
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])


def call_llm(user_text: str) -> str:
    mode = st.session_state.mode
    profile = st.session_state.profile

    system_prompt = build_system_prompt(mode, profile)

    # 대화 히스토리 (최근 몇 개만 넣어도 됨)
    history = st.session_state.chat[-12:]  # 너무 길어지는 거 방지
    api_messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_text}]

    # 최신 방식: responses.create
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=api_messages,
    )
    return response.output_text.strip()


# -------------------------
# 3) UI
# -------------------------
ensure_session_state()

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("System Mode (by digital infrastructure)")
    st.session_state.mode = st.selectbox(
        " ",
        ["Low-infrastructure (Voice/Simple)", "High-infrastructure (Personalized)"],
        index=0 if "Low-infrastructure" in st.session_state.mode else 1
    )

    st.divider()
    st.subheader("Student profile")

    goal = st.text_input("Goal (e.g., raise math score to 80)", value=st.session_state.profile["goal"])
    daily_time = st.selectbox("Daily study time", ["10–20 min", "20–40 min", "40–60 min", "60+ min"],
                              index=["10–20 min", "20–40 min", "40–60 min", "60+ min"].index(st.session_state.profile["daily_time"]))
    level = st.selectbox("Self-reported level", ["Beginner", "Intermediate", "Advanced"],
                         index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.profile["level"]))

    st.session_state.profile = {"goal": goal, "daily_time": daily_time, "level": level}

    if st.button("Reset chat"):
        st.session_state.chat = []
        st.rerun()

with right:
    st.title("📚 JSS: AI Study Advisor")
    st.caption("A level-based study counseling chatbot (demo).")

    # 첫 메시지(없을 때만)
    if len(st.session_state.chat) == 0:
        st.session_state.chat.append({
            "role": "assistant",
            "content": "Hi! I’m JSS. Tell me what you’re struggling with, and I’ll help you make a simple plan."
        })

    render_chat()

    user_input = st.chat_input("Type your message...")
    if user_input:
        # user message 저장
        st.session_state.chat.append({"role": "user", "content": user_input})

        # assistant 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = call_llm(user_input)
                except Exception as e:
                    reply = f"Sorry—an error occurred. ({type(e).__name__}) Please try again."
            st.markdown(reply)

        st.session_state.chat.append({"role": "assistant", "content": reply})
