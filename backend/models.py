from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any


class ChatRequest(BaseModel):
    conversation_id: str
    user_message: str


class SuggestedReply(BaseModel):
    text: str


# ---------------- NOVO IME ----------------
class TaskRecommendation(BaseModel):
    task: str           # npr. “Napiši uvod od 300 riječi”
    score: float        # ili važnost / prioritet (0‑1) – po želji
# ------------------------------------------


class SuggestedAction(BaseModel):
    text: str
    action: Literal["add_task"]
    payload: Dict[str, Any]


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    # ⇩ stari naziv zamijenjen novim
    recommended_tasks: Optional[List[TaskRecommendation]] = None
    suggested_replies: Optional[List[SuggestedReply]] = None
    suggested_actions: Optional[List[SuggestedAction]] = None
