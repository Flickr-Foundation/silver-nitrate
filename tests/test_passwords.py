"""
Tests for ``nitrate.passwords``.
"""

import keyring
from nitrate.passwords import use_in_memory_keyring


def test_gets_existing_password() -> None:
    """
    Getting a password with ``get_password`` will succeed if you're
    using an in-memory keyring.
    """
    use_in_memory_keyring(initial_passwords={("flickr", "api_key"): "12345"})

    assert keyring.get_password("flickr", "api_key") == "12345"
