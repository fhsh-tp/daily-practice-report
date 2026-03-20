"""Gravatar URL helper and Jinja2 filter."""
import hashlib


def gravatar_url(email: str | None, size: int = 40) -> str:
    """Return a Gravatar avatar URL for *email*.

    - Non-empty email  → ``https://www.gravatar.com/avatar/<md5>?d=identicon``
    - Empty / None     → ``https://www.gravatar.com/avatar/?d=identicon``
    """
    if not email:
        return "https://www.gravatar.com/avatar/?d=identicon"
    digest = hashlib.md5(email.strip().lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?d=identicon"
