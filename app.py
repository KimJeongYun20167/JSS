import streamlit as st

st.set_page_config(page_title="JSS Study Advisor", page_icon="📚")
st.title("📚 JSS: AI Study Advisor")
st.caption("A level-based study counseling chatbot (demo).")

# 1) 모드 선택 (디지털 인프라 수준에 따른 버전)
mode = st.sidebar.selectbox(
    "System Mode (by digital infrastructure)",
    ["Low-infrastructure (Voice/Simple)", "High-infrastructure (Personalized)"]
)

# 2) 대화 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’m JSS. Tell me what you’re struggling with."}
    ]

# 3) 기존 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4) 사용자 입력
user_text = st.chat_input("Type your message...")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    # 5) 간단한 응답 로직 (시뮬레이션)
    def jss_reply(text: str, mode: str) -> str:
        t = text.lower()

        # 대표 질문: 성적이 안 오름
        if "grades" in t or "improve" in t or "성적" in text or "안 오르" in text:
            if "Low-infrastructure" in mode:
                return (
                    "I understand. Let’s start small: choose ONE topic you find hardest today. "
                    "I’ll ask a simple question and guide you step by step."
                )
            else:
                return (
                    "I get it. Let’s adjust your plan: we’ll identify your weak areas, "
                    "change your review schedule, and track progress this week."
                )

        # 공부 계획
        if "plan" in t or "schedule" in t or "계획" in text:
            if "Low-infrastructure" in mode:
                return "Let’s make a simple plan: 20 minutes study + 5 minutes break, repeat 3 times."
            else:
                return "Tell me your goal and current level. I’ll generate a personalized weekly plan."

        # 기본 fallback
        if "Low-infrastructure" in mode:
            return "Thanks. Tell me one subject you want to focus on today."
        else:
            return "Thanks. What subject, goal, and recent scores do you have? I’ll tailor advice."

    reply = jss_reply(user_text, mode)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # 화면 즉시 갱신
    st.rerun()
