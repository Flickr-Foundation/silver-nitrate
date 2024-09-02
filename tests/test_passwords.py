"""
Tests for ``nitrate.passwords``.
"""

import pytest

from nitrate.passwords import get_required_password, use_in_memory_keyring


def test_gets_existing_password() -> None:
    """
    Getting a password with ``get_required_password`` will succeed if
    the password exists.
    """
    use_in_memory_keyring(initial_passwords={("flickr", "api_key"): "12345"})

    assert get_required_password("flickr", "api_key") == "12345"


def test_throws_if_password_does_not_exist() -> None:
    """
    Trying to get a non-existent password with ``get_required_password``
    will throw a ``RuntimeError``.
    """
    with pytest.raises(RuntimeError, match="Could not retrieve password"):
        get_required_password("doesnotexist", "doesnotexist")
