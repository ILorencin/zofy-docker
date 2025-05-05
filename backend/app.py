# api.py — main FastAPI application
# -------------------------------------------------
from fastapi import FastAPI
from models import ChatRequest, ChatResponse, SuggestedReply, SuggestedAction
from coach import (
    coach,
    generate_growth_tasks,
    reframe_negative_thought_multi,   # returns (lead, options)
)
from intent import detect_intent
from suggested import generate_suggested_replies
from user_profile import user_profile
from prompts import SURVIVAL
from startup import generate_initial_greeting, generate_initial_suggested_replies

app = FastAPI()
conversation_states: dict[str, dict[str, list[str]]] = {}


# -------------------- HELPERS --------------------
def _update_history(cid: str, msg: str) -> None:
    conversation_states.setdefault(cid, {"user_messages": []})
    conversation_states[cid]["user_messages"].append(msg)


def _history_str(cid: str) -> str:
    return "\n".join(conversation_states[cid]["user_messages"])


def _extract_tasks(text: str) -> list[str]:
    """Rough heuristic: any line with ≥3 words is treated as a task."""
    lines = [l.strip("-•0123456789. ").rstrip() for l in text.splitlines() if l.strip()]
    return [l for l in lines if len(l.split()) >= 3]


# ========= INTERNAL SHARED CHAT HANDLER ==========
def _handle_chat(req: ChatRequest, forced_time: str | None = None) -> ChatResponse:
    """
    forced_time: 'morning' | 'afternoon' | 'evening' | None
    """
    cid, user_msg = req.conversation_id, req.user_message
    conversation_states.setdefault(cid, {"user_messages": []})

    # 1️⃣ First message → dynamic greeting
    if not conversation_states[cid]["user_messages"]:
        _update_history(cid, user_msg)
        greeting = generate_initial_greeting(user_profile, time_block=forced_time)
        suggestions = generate_initial_suggested_replies(user_profile, time_block=forced_time)
        return ChatResponse(
            reply=greeting,
            conversation_id=cid,
            suggested_replies=[SuggestedReply(text=s) for s in suggestions],
        )

    # 2️⃣ Subsequent messages
    _update_history(cid, user_msg)
    hist = _history_str(cid)
    intent = detect_intent(user_msg)
    print("Detected intent:", intent, "| forced_time:", forced_time)

    # ---- REFRAME ------------------------------------------------------
    if intent == "reframe":
        lead, opts = reframe_negative_thought_multi(
            negative_thought=user_msg,
            user_profile=user_profile,
            context=hist,
            num_options=10,
        )
        return ChatResponse(
            reply=lead,
            conversation_id=cid,
            suggested_replies=[SuggestedReply(text=o) for o in opts],
        )

    # ---- GROWTH TASKS -------------------------------------------------
    if intent == "growth_tasks":
        reply_text = generate_growth_tasks(user_msg, user_profile, hist)
    else:  # normal chat
        reply_text = coach(
            hist,
            user_msg,
            profile=user_profile,
            context=SURVIVAL,
            try_auto_tasks=False,
        )

    # NEW SIGNATURE   ↓↓↓
    suggested = generate_suggested_replies(
        user_msg,
        reply_text,
        num_replies=3,
        user_profile=user_profile,
        level=SURVIVAL,
        time_block=forced_time or "afternoon",
    )

    # Quick‑action buttons only for explicit growth‑task requests
    actions = None
    if intent == "growth_tasks":
        tasks = _extract_tasks(reply_text)
        if tasks:
            actions = [
                SuggestedAction(
                    text=f"✅ Add: {t[:40]}…" if len(t) > 43 else f"✅ Add: {t}",
                    action="add_task",
                    payload={"task": t, "conversation_id": cid},
                )
                for t in tasks
            ]

    return ChatResponse(
        reply=reply_text,
        conversation_id=cid,
        suggested_replies=[SuggestedReply(text=s) for s in suggested],
        suggested_actions=actions,
    )
# =================================================


# ------------------- CHAT ENDPOINTS --------------
@app.post("/chat", response_model=ChatResponse)  # default = afternoon
def chat_default(req: ChatRequest) -> ChatResponse:
    return _handle_chat(req, forced_time="afternoon")


@app.post("/chat/morning", response_model=ChatResponse)
def chat_morning(req: ChatRequest) -> ChatResponse:
    return _handle_chat(req, forced_time="morning")


@app.post("/chat/afternoon", response_model=ChatResponse)
def chat_afternoon(req: ChatRequest) -> ChatResponse:
    return _handle_chat(req, forced_time="afternoon")


@app.post("/chat/evening", response_model=ChatResponse)
def chat_evening(req: ChatRequest) -> ChatResponse:
    return _handle_chat(req, forced_time="evening")
# -------------------------------------------------


# -------------------- REFRAME --------------------
@app.post("/reframe", response_model=ChatResponse)
def reframe_endpoint(req: ChatRequest) -> ChatResponse:
    cid, user_msg = req.conversation_id, req.user_message
    _update_history(cid, user_msg)
    hist = _history_str(cid)

    lead, opts = reframe_negative_thought_multi(
        negative_thought=user_msg,
        user_profile=user_profile,
        context=hist,
        num_options=10,
    )
    return ChatResponse(
        reply=lead,
        conversation_id=cid,
        suggested_replies=[SuggestedReply(text=o) for o in opts],
    )
# -------------------------------------------------


# ---------------- GROWTH TASKS -------------------
@app.post("/growth_tasks", response_model=ChatResponse)
def growth_tasks_endpoint(req: ChatRequest) -> ChatResponse:
    # Always treated as an afternoon flow
    return _handle_chat(req, forced_time="afternoon")
# -------------------------------------------------


# -------- MOCK ENDPOINT FOR “ADD TASK” -----------
@app.post("/tasks/add")
def add_task_endpoint(
    cid: str | None = None,
    conversation_id: str | None = None,
    task: str | None = None,
) -> dict:
    cid = cid or conversation_id or "mock"
    if not task:
        return {"status": "accepted", "cid": cid, "warning": "task missing"}
    return {"status": "accepted", "cid": cid, "task": task}
# -------------------------------------------------
