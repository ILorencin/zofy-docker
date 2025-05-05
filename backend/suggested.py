# suggested.py  – generate quick‑reply buttons
# -------------------------------------------------
import json
from datetime import datetime
import openai
from example_suggestions import SUGGESTION1

# 🆕  full set of few‑shot examples
from time_flows.conversations import (
    EXAMPLE_CONVERSATIONS,
    EXAMPLE_MORNING,
    EXAMPLE_EVENING,
)


# ---------- utilities --------------------------------------------------
def _join(items):          # helper to stringify lists
    return ", ".join(items) if items else "None"


def _detect_time_block(now: datetime | None = None) -> str:
    h = (now or datetime.now()).hour
    return "morning" if 5 <= h < 12 else "afternoon" if h < 18 else "evening"
# ----------------------------------------------------------------------


def generate_suggested_replies(
    user_msg: str,
    final_answer: str,
    num_replies: int = 3,
    *,
    user_profile: dict | None = None,
    level: str | None = None,
    time_block: str | None = None,
) -> list[str]:
    """
    Returns `num_replies` concise follow‑up messages the USER might type next,
    tuned to time of day and consciousness level.
    """

    # -------- 1) profile text -----------------------------------------
    profile_text = ""
    if user_profile:
        profile_text = f"""
[USER PROFILE]
Name:  {user_profile.get('ime', 'N/A')}
Goals: {_join(user_profile.get('ciljevi', []))}
Priorities: {_join(user_profile.get('prioriteti', []))}
Values: {_join(user_profile.get('osobne_vrijednosti', []))}
"""

    # -------- 2) time‑block selection ---------------------------------
    time_block = (time_block or _detect_time_block()).lower()
    examples_block = {
        "morning": EXAMPLE_MORNING,
        "evening": EXAMPLE_EVENING,
    }.get(time_block, EXAMPLE_CONVERSATIONS)

    tone_hint = {
        "morning":   "It's morning – keep it fresh, energising, intention‑setting.",
        "afternoon": "It's afternoon – encourage momentum, focus and practical action.",
        "evening":   "It's evening – gentle, reflective, winding‑down tone.",
    }[time_block]

    # -------- 3) system prompt ----------------------------------------
    system_prompt = f"""
You are Zofy, a compassionate female self‑growth coach.

GOAL
----
Provide {num_replies} SHORT follow‑up replies that **the user** could send next.
They should feel natural, encourage deeper conversation, and relate to personal growth.

CONSTRAINTS
-----------
* 1 sentence each, ≤ 12 words when possible.
* Write them as USER messages (first‑person), not as Zofy.
* Fit consciousness level: {level or 'unknown'}.
* {tone_hint}
* No numbering / bullets.

FEW‑SHOT STYLE EXAMPLES (adapted to time block)
----------------------------------------------
{examples_block}

REFERENCE EXAMPLE OF A SINGLE SUGGESTION
----------------------------------------
{SUGGESTION1}

{profile_text}
"""

    # -------- 4) call LLM --------------------------------------------
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"User's last message:\n{user_msg}\n\n"
                f"Zofy's answer:\n{final_answer}\n\n"
                f"Now propose {num_replies} follow‑up replies."
            ),
        },
    ]

    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
    )
    raw = resp["choices"][0]["message"]["content"].strip()

    # -------- 5) cleanup & return ------------------------------------
    suggestions = [
        line.strip("-•*0123456789). ").rstrip()
        for line in raw.splitlines() if line.strip()
    ][:num_replies]

    return suggestions
# -------------------------------------------------
