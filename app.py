import streamlit as st

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="JSS Study Advisor", page_icon="📚", layout="centered")
st.title("📚 JSS: AI Study Advisor")
st.caption("A level-based study counseling chatbot (demo).")

# ----------------------------
# Sidebar: mode + controls
# ----------------------------
mode = st.sidebar.selectbox(
    "System Mode (by digital infrastructure)",
    ["Low-infrastructure (Voice/Simple)", "High-infrastructure (Personalized)"]
)

st.sidebar.markdown("---")

# Reset button (very useful for demos)
if st.sidebar.button("Reset chat"):
    st.session_state.clear()
    st.rerun()

# Example buttons (demo-friendly)
st.sidebar.subheader("Quick demo prompts")
if st.sidebar.button("Example: Grades not improving"):
    st.session_state.demo_input = "I've been studying, but my grades don't seem to improve."
    st.rerun()

if st.sidebar.button("Example: I feel stressed"):
    st.session_state.demo_input = "I feel stressed and unmotivated."
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("Tip: Low-infrastructure mode uses shorter, simpler coaching.")


# ----------------------------
# Initialize session state
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’m JSS. Tell me what you’re struggling with."}
    ]

# Conversation stage:
# ask_subject -> ask_level -> coaching
if "stage" not in st.session_state:
    st.session_state.stage = "ask_subject"

if "subject" not in st.session_state:
    st.session_state.subject = None

if "level" not in st.session_state:
    st.session_state.level = None


# ----------------------------
# Core reply logic with stages
# ----------------------------
def jss_reply(text: str, mode: str) -> str:
    t = text.strip()
    tl = t.lower()

    subjects = {"math", "reading", "science"}
    levels = {"beginner", "intermediate", "advanced"}

    # --- Stage 1: Ask subject ---
    if st.session_state.stage == "ask_subject":
        # accept slightly flexible inputs
        if tl in subjects:
            st.session_state.subject = tl
            st.session_state.stage = "ask_level"
            return f"Got it — {tl.title()}. What’s your current level? (Beginner / Intermediate / Advanced)"
        else:
            return "Tell me one subject you want to focus on today. (Math / Reading / Science)"

    # --- Stage 2: Ask level ---
    if st.session_state.stage == "ask_level":
        if tl in levels:
            st.session_state.level = tl
            st.session_state.stage = "coaching"

            if "Low-infrastructure" in mode:
                return (
                    f"Okay. {st.session_state.subject.title()} ({tl}). "
                    "Let’s start small: 1 concept + 3 practice questions.\n"
                    "What topic is hardest for you? (e.g., fractions, equations)"
                )
            else:
                return (
                    f"Great. {st.session_state.subject.title()} ({tl}). "
                    "What topic is hardest for you? (e.g., fractions, equations)\n"
                    "Also, what score/grade are you aiming for?"
                )
        else:
            return "Choose one level: Beginner / Intermediate / Advanced"

    # --- Stage 3: Coaching ---
    if st.session_state.stage == "coaching":
        # Special case: grades not improving
        if ("grades" in tl) or ("improve" in tl) or ("score" in tl) or ("성적" in t) or ("안 오르" in t):
            if "Low-infrastructure" in mode:
                return (
                    "I understand.\n"
                    "Today: pick ONE weak topic, do 5 questions, and review mistakes.\n"
                    "What topic should we start with?"
                )
            else:
                return (
                    "I understand how that feels.\n"
                    "Let’s adjust your plan: focus on weak areas + spaced review + error log.\n"
                    "Tell me your weak topic and your recent score."
                )

        # Special case: stress / emotion
        if ("stress" in tl) or ("anxious" in tl) or ("tired" in tl) or ("무기력" in t) or ("불안" in t) or ("스트레스" in t):
            if "Low-infrastructure" in mode:
                return (
                    "That sounds hard.\n"
                    "Let’s set a tiny goal: 10 minutes study + 3 questions.\n"
                    "After that, tell me: easy or hard?"
                )
            else:
                return (
                    "That sounds stressful.\n"
                    "Let’s reduce today’s load and set one clear goal.\n"
                    "What is the hardest topic right now, and how long can you study today?"
                )

        # Default coaching response (simple plan)
        if "Low-infrastructure" in mode:
            return (
                "Thanks. Here’s a simple plan:\n"
                "1) Review 10 min\n"
                "2) Practice 5 questions\n"
                "3) Check mistakes 5 min\n"
                "Tell me if you want more practice questions."
            )
        else:
            return (
                "Thanks. Here’s a basic plan:\n"
                "1) Review the concept (15 min)\n"
                "2) Solve 10 questions (20 min)\n"
                "3) Error log: write 3 mistake notes (10 min)\n"
                "Want a weekly plan too? (Yes/No)"
            )

    # Fallback (shouldn't happen)
    return "Tell me what you want to learn today."


# ----------------------------
# Render message history
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ----------------------------
# Input box (chat)
# ----------------------------
# If user clicked demo buttons, prefill once
prefill = st.session_state.pop("demo_input", None)

user_text = st.chat_input("Type your message...") if prefill is None else prefill

if user_text:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Generate reply
    reply = jss_reply(user_text, mode)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.rerun()
