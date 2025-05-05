from user_profile import user_profile

# Extract the name from the current user profile (located under "Basic Info")
name = user_profile.get("Basic Info", {}).get("Name", "there")
STARTING_MESSAGE = f"Hi {name}! How can I help you today :)?"
