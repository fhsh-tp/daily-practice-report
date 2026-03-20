"""Unit tests for the gravatar_url Jinja2 filter (Task 5.1)."""
import hashlib


def test_gravatar_url_with_email():
    """Email set → URL uses md5(email.strip().lower())."""
    from shared.gravatar import gravatar_url

    email = "Test@Example.com"
    expected_hash = hashlib.md5("test@example.com".encode()).hexdigest()
    url = gravatar_url(email)
    assert url == f"https://www.gravatar.com/avatar/{expected_hash}?d=identicon"


def test_gravatar_url_strips_and_lowercases():
    """Email with whitespace and uppercase → normalised before hashing."""
    from shared.gravatar import gravatar_url

    url1 = gravatar_url("  alice@example.com  ")
    url2 = gravatar_url("ALICE@EXAMPLE.COM")
    assert url1 == url2


def test_gravatar_url_with_empty_string():
    """Empty email → identicon fallback URL."""
    from shared.gravatar import gravatar_url

    url = gravatar_url("")
    assert url == "https://www.gravatar.com/avatar/?d=identicon"


def test_gravatar_url_with_none():
    """None email → identicon fallback URL."""
    from shared.gravatar import gravatar_url

    url = gravatar_url(None)
    assert url == "https://www.gravatar.com/avatar/?d=identicon"
