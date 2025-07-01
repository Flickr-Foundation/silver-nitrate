"""
Tests for `nitrate.mock_keyring`.
"""

import keyring
from keyring.backend import KeyringBackend

from nitrate.mock_keyring import *  # noqa: F403


def test_mock_keyring(mock_keyring: KeyringBackend) -> None:
    """
    The mock keyring allows you to set and retrieve passwords.
    """
    assert keyring.get_password("testing", "example_password") is None
    mock_keyring.set_password("testing", "example_password", "12345")
    assert keyring.get_password("testing", "example_password") == "12345"
