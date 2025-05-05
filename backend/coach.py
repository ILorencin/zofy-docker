import openai
import json
from datetime import datetime

# Import level instructions from levels.py
from levels import level1, level2, level3, level4, level5, level6, level7, level8
import openai
import json
from user_profile import user_profile 


def get_level_instruction(user_profile: dict) -> str:
    """
    Returns the level instruction string based on the user's current level,
    extracted from the user profile.
    """
    try:
        current_level = user_profile.get("Consciousness Level", {}).get("Current Level", "")
    except AttributeError:
        return "No level instruction available."

    # Determine which level instruction to use based on current_level text.
    if "Level 1" in current_level:
        return level1
    elif "Level 2" in current_level:
        return level2
    elif "Level 3" in current_level:
        return level3
    elif "Level 4" in current_level:
        return level4
    elif "Level 5" in current_level:
        return level5
    elif "Level 6" in current_level:
        return level6
    elif "Level 7" in current_level:
        return level7
    elif "Level 8" in current_level:
        return level8
    else:
        return "No specific level instruction available."

# -*- coding: utf-8 -*-
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import openai

from levels import level1, level2, level3, level4, level5, level6, level7, level8
from user_profile import user_profile  # ili tvoj loader

# -----------  TIME-OF-DAY FLOWS  -----------------
from time_flows.morning import MORNING_SYSTEM_TEMPLATE
from time_flows.afternoon import AFTERNOON_SYSTEM_TEMPLATE
from time_flows.evening import EVENING_SYSTEM_TEMPLATE
# -------------------------------------------------

# -----------  HELPERI  -----------------
LEVEL_MAP = {
    "Level 1": level1,
    "Level 2": level2,
    "Level 3": level3,
    "Level 4": level4,
    "Level 5": level5,
    "Level 6": level6,
    "Level 7": level7,
    "Level 8": level8,
}

def get_level_instruction(profile: dict) -> str:
    lvl = profile.get("Consciousness Level", {}).get("Current Level", "")
    return next((text for key, text in LEVEL_MAP.items() if key in lvl), "")

def get_time_block(now: Optional[datetime] = None) -> str:
    """Vrati 'morning', 'afternoon' ili 'evening'."""
    now = now or datetime.now()
    h = now.hour
    if 5 <= h < 12:
        return "morning"
    if 12 <= h < 18:
        return "afternoon"
    return "evening"

TIME_TEMPLATES = {
    "morning": MORNING_SYSTEM_TEMPLATE,
    "afternoon": AFTERNOON_SYSTEM_TEMPLATE,
    "evening": EVENING_SYSTEM_TEMPLATE,
}

# ---------------------------------------


def coach(
    history: str,
    user_message: str,
    profile: Optional[dict] = None,
    context: str = "",
    try_auto_tasks: bool = True,
) -> str:
    profile = profile or {}
    time_block = get_time_block()
    system_template = TIME_TEMPLATES[time_block]

    system_prompt = f"""{system_template}

User profile:
{json.dumps(profile, indent=2)}

Level instruction:
{get_level_instruction(profile)}

Conversation so far:
{history}

Additional context:
{context}

Now answer the user's new message:
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
    )
    assistant_reply = response["choices"][0]["message"]["content"]

    # --------------  AUTO-TASK GENERATOR  -----------------
    if try_auto_tasks and _needs_task_generation(user_message):
        tasks = generate_growth_tasks(
            challenge_or_goal=_extract_goal(user_message),
            user_profile=profile,
            context=context,
        )
        assistant_reply += (
            "\n\n---\nEvo nekoliko konkretnih zadataka koji ti mogu pomoći:\n"
            f"{tasks}"
        )
    # ------------------------------------------------------

    return assistant_reply


def _needs_task_generation(message: str) -> bool:
    """
    Jednostavan heuristički detektor.
    Ako poruka sadrži riječi 'task', 'zadatak', 'plan', 'goal'… vrati True.
    Po potrebi zamijeni regexom ili OpenAI-callom za semantičko prepoznavanje.
    """
    triggers = ["task", "zadatak", "plan", "goal", "challenge", "prioritet"]
    message_lower = message.lower()
    return any(t in message_lower for t in triggers)


def _extract_goal(message: str) -> str:
    """
    Placeholder – u praksi možeš:
      * parsirati zadnje korisničke rečenice,
      * ili upotrijebiti manji LLM-call za “goal extraction”.
    Za demo ćemo vratiti cijelu poruku.
    """
    return message.strip()


def reframe_negative_thought_multi(
    negative_thought: str,
    user_profile: dict | None = None,
    context: str | None = None,
    num_options: int = 10,
) -> tuple[str, list[str]]:
    """
    Generates a gentle “lead‑in” line + a list of positive reframes.
    
    Returns
    -------
    (lead_text, options)
        lead_text : str
            Soft, Zofy‑style invitation shown above the buttons.
        options   : list[str]
            Exactly `num_options` one‑line reframes (1st‑person, no numbering).
    """
    # -------- defaults --------------------------------------------------
    context = context or "No specific context provided."
    user_profile = user_profile or {}

    # -------- prepare prompt -------------------------------------------
    profile_text      = json.dumps(user_profile, indent=2)
    level_instruction = get_level_instruction(user_profile)

    system_prompt = f"""
You are Zofy, a compassionate and insightful mental‑wellness assistant.
Your task is to help users reframe a negative thought into positive,
realistic and emotionally supportive alternatives.

Guidelines:
- Offer exactly {num_options} alternative reframes of the negative thought.
- Each reframe is short, positive and in the first person.
- Acknowledge struggle gently; avoid toxic positivity.
- One suggestion per line, with no numbering, bullets or intro text.
- Follow this level‑based instruction: {level_instruction}

User Profile:
{profile_text}

User Context:
{context}

Negative thought to reframe:
"{negative_thought}"
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": negative_thought},
        ],
        temperature=0.7,
    )

    raw = response["choices"][0]["message"]["content"]

    # -------- clean output ---------------------------------------------
    options = [
        line.strip("-•0123456789. ").rstrip()
        for line in raw.splitlines()
        if line.strip()
    ][:num_options]

    # -------- soft lead‑in ---------------------------------------------
    lead_text = (
        "I feel how heavy that thought is. "
        "Here are a few kinder ways you might speak to yourself—"
        "pick the one that feels right:"
    )

    return lead_text, options


def generate_growth_tasks(
    challenge_or_goal: str,
    user_profile: Optional[dict] = None,
    context: str = ""
) -> str:
    user_profile = user_profile or {}
    profile_text = json.dumps(user_profile, indent=2)
    level_instruction = get_level_instruction(user_profile)

    system_prompt = f"""
You are Zofy, a thoughtful and supportive self-growth coach.
Follow this level-based instruction: {level_instruction}

User Profile:
{profile_text}

User Context:
{context}

User's current challenge or goal:
"{challenge_or_goal}"

Instructions:
- Generate 3 to 5 actionable and realistic tasks.
- Each task should be described in 1-2 sentences.
- Tasks should promote growth in mindset, habits, or emotional well-being.
- Make them motivational, but not overwhelming.
- Adapt the tone and content to the user's background if available.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": challenge_or_goal},
        ],
        temperature=0.8,
    )
    return response["choices"][0]["message"]["content"]
