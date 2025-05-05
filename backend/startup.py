# startup.py  – helper functions for the very first turn
# ------------------------------------------------------
import json
import openai
from datetime import datetime
from user_profile import user_profile   # your own loader

# --------- (optional) level references, if you need them later ----------
from levels import (
    level1, level2, level3, level4, level5, level6, level7, level8,
)
# -----------------------------------------------------------------------


# --------- GREETING ----------------------------------------------------
def generate_initial_greeting(
    user_profile: dict,
    time_block: str | None = None,   # 'morning' | 'afternoon' | 'evening' | None
) -> str:
    """
    Return a warm, personalised greeting.  
    • time_block tweaks the tone; if None, afternoon / neutral style is used.
    """
    time_block = (time_block or "afternoon").lower()
    profile_json = json.dumps(user_profile, indent=2)

    system_prompt = f"""
You are Zofy, an empathetic self‑growth coach.

TASK
-----
Generate a short, first‑message greeting for a brand‑new conversation.

CONSTRAINTS
-----------
* Must be friendly, warm and encouraging.
* Address the user by name if available.
* Reflect an understanding of their background and goals (see profile).
* Adapt the tone to the time of day:  
  - MORNING  → energising, fresh‑start vibe  
  - AFTERNOON→ motivating, momentum‑building  
  - EVENING  → calm, reflective, winding‑down
* Output **only** the greeting sentence(s); no bullet points or meta‑text.

TIME OF DAY = {time_block.upper()}

USER PROFILE (JSON)
-------------------
{profile_json}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        temperature=0.7,
        max_tokens=120,
    )
    return response["choices"][0]["message"]["content"].strip()
# -----------------------------------------------------------------------


# --------- SUGGESTED REPLIES -------------------------------------------
def generate_initial_suggested_replies(
    user_profile: dict,
    time_block: str | None = None,
    num_suggestions: int = 4,
) -> list[str]:
    """
    Produce `num_suggestions` short user‑side replies that could naturally
    follow the greeting.
    """
    time_block = (time_block or "afternoon").lower()
    profile_json = json.dumps(user_profile, indent=2)

    system_prompt = f"""
You are Zofy, a compassionate self‑growth coach.

TASK
-----
Create {num_suggestions} concise replies that **the user** might choose
to continue the conversation **after Zofy greets them**.

CONSTRAINTS
-----------
* Each reply is ONE sentence, < 15 words if possible.
* They should invite meaningful dialogue (e.g., asking for help, sharing a goal).
* Do NOT prefix with numbering, bullets or quotation marks.
* Tailor wording to the user's background.
* Tone should fit the time block: {time_block}.

USER PROFILE (JSON)
-------------------
{profile_json}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        temperature=0.7,
        max_tokens=120,
    )
    raw = response["choices"][0]["message"]["content"]

    # clean & return exactly `num_suggestions`
    suggestions = [
        line.strip("-•* ").rstrip()
        for line in raw.splitlines()
        if line.strip()
    ][:num_suggestions]
    return suggestions
# -----------------------------------------------------------------------


# -------------------------- DEMO ---------------------------------------
if __name__ == "__main__":
    for tb in ("morning", "afternoon", "evening"):
        print(f"\n=== {tb.upper()} ===")
        g = generate_initial_greeting(user_profile, time_block=tb)
        s = generate_initial_suggested_replies(user_profile, time_block=tb)
        print("Greeting:", g)
        print("Suggested replies:")
        for line in s:
            print("  •", line)
