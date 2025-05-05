import openai

def detect_intent(user_message: str) -> str:
    system_instructions = (
        "You are a classification system that routes user input into one of three categories:\n"
        "1. chat - if the user just wants to talk, reflect, or explore a thought.\n"
        "2. reframe - if the user expresses a clearly negative thought that could be turned into a positive one.\n"
        "3. growth_tasks - if the user is asking for help with progress, change, or concrete actions for self-development.\n\n"
        "Respond with ONLY one of the following: chat, reframe, or growth_tasks."
    )

    messages = [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": user_message}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        max_tokens=10
    )

    result = response["choices"][0]["message"]["content"].strip().lower()
    if result not in {"chat", "reframe", "growth_tasks"}:
        return "chat"  # fallback
    return result
