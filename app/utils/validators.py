from typing import Optional

BANNED_WORDS = {"spam", "offensive", "banned"}

def check_message_content(content: str) -> Optional[str]:
    lowered = content.lower()
    for word in BANNED_WORDS:
        if word in lowered:
            return f"Message contains banned word: {word}"
    return None 