# frontend.py – Streamlit client for Zofy
# -------------------------------------------------
import streamlit as st
import requests

st.set_page_config(page_title="Zofy AI", page_icon="🌱", layout="centered")
st.title("Zofy AI – your self‑growth assistant")

# ---------- 1) SESSION STATE ----------
defaults = {
    "conversation": [],
    "conversation_id": "conv1",
    "last_suggested_replies": [],
    "last_suggested_actions": [],
    "active_tasks": [],
    "interaction_type": "chat",
    "chat_time": "afternoon",   # 🌞 / 🌤️ / 🌙  (default)
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)
# ---------------------------------------

CHAT_INPUT_KEY = "chat_input_key"


# ---------- 2) SEND MESSAGE ----------
def send_message():
    user_text = st.session_state.get(CHAT_INPUT_KEY, "").strip()
    if not user_text:
        return

    # choose endpoint -----------------------------------------------
    chat_time = st.session_state.get("chat_time", "afternoon")
    if st.session_state["interaction_type"] == "chat":
        path = {"morning": "chat/morning",
                "afternoon": "chat",
                "evening": "chat/evening"}[chat_time]
        url = f"http://backend:8000/{path}"
    else:
        url = {
            "reframe": "http://backend:8000/reframe",
            "growth_tasks": "http://backend:8000/growth_tasks",
        }[st.session_state["interaction_type"]]

    payload = {
        "conversation_id": st.session_state["conversation_id"],
        "user_message": user_text,
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        st.session_state["conversation"].append({"role": "user", "content": user_text})
        st.session_state["conversation"].append({"role": "assistant", "content": data.get("reply", "")})

        raw_replies = data.get("suggested_replies", [])
        st.session_state["last_suggested_replies"] = [
            r["text"] if isinstance(r, dict) else str(r) for r in raw_replies
        ]
        st.session_state["last_suggested_actions"] = data.get("suggested_actions", [])

    except requests.exceptions.RequestException as e:
        st.error(f"Backend error: {e}")

    st.session_state[CHAT_INPUT_KEY] = ""
# ------------------------------------------------------------------


# ---------- 3) CLEAR / SUGGESTION ----------
def clear_conversation():
    st.session_state["conversation"] = []
    st.session_state["last_suggested_replies"] = []
    st.session_state["last_suggested_actions"] = []
    st.session_state["active_tasks"] = []
    st.session_state["chat_time"] = "afternoon"
    st.session_state[CHAT_INPUT_KEY] = ""


def use_suggestion(text: str):
    st.session_state[CHAT_INPUT_KEY] = text
    send_message()
    st.rerun()
# ------------------------------------------------------------------


# ---------- 4) ACTION CALLBACK ----------
def perform_action(action_dict):
    """Call /tasks/add and refresh active task list."""
    try:
        r = requests.post("http://backend:8000/tasks/add", params=action_dict["payload"])
        r.raise_for_status()
        data = r.json()
        st.session_state["active_tasks"] = data.get("tasks", [])
        st.success("Task added!")
    except requests.exceptions.RequestException as e:
        st.error(f"Cannot add task: {e}")
# ------------------------------------------------------------------


# ---------- 5) UI ----------
st.button("🧹 Clear Conversation", on_click=clear_conversation)

st.radio(
    "Choose mode:",
    ["chat", "reframe", "growth_tasks"],
    key="interaction_type",
    format_func=lambda x: {
        "chat": "🗣️ Chat",
        "reframe": "🔄 Reframe thought",
        "growth_tasks": "🚀 Growth tasks",
    }[x],
)

if st.session_state["interaction_type"] == "chat":
    st.radio(
        "Time of day:",
        ["morning", "afternoon", "evening"],
        key="chat_time",
        format_func=lambda x: {
            "morning": "🌞 Morning",
            "afternoon": "🌤️ Afternoon",
            "evening": "🌙 Evening",
        }[x],
        horizontal=True,
    )
    st.write("")

st.text_input("Your message", key=CHAT_INPUT_KEY, placeholder="Type here...")
st.button("Send", on_click=send_message)

st.divider()

# conversation messages
for msg in st.session_state["conversation"]:
    role = "You" if msg["role"] == "user" else "Zofy AI"
    st.markdown(f"**{role}:** {msg['content']}")

# suggested replies
if st.session_state["last_suggested_replies"]:
    st.markdown("**Suggested replies:**")
    for i, s in enumerate(st.session_state["last_suggested_replies"]):
        st.button(s, key=f"rep_{i}", on_click=use_suggestion, args=(s,))

# quick actions
if st.session_state["last_suggested_actions"]:
    st.markdown("**Quick actions:**")
    for i, act in enumerate(st.session_state["last_suggested_actions"]):
        st.button(
            act["text"],
            key=f"act_{i}",
            on_click=perform_action,
            args=(act,),
        )

# active tasks
if st.session_state["active_tasks"]:
    st.markdown("### 📌 Active Tasks")
    for t in st.session_state["active_tasks"]:
        st.markdown(f"- {t}")
# ------------------------------------------------------------------
