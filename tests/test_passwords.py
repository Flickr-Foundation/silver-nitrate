import keyring
import pytest

from nitrate.passwords import InMemoryKeyring, get_required_password


class TestGetRequiredPassword:
    def test_gets_existing_password(self) -> None:
        keyring.set_keyring(InMemoryKeyring())
        keyring.set_password("flickr", "api_key", "12345")

        assert get_required_password("flickr", "api_key") == "12345"

    def test_throws_if_password_does_not_exist(self) -> None:
        keyring.set_keyring(InMemoryKeyring())

        with pytest.raises(RuntimeError, match="Could not retrieve password"):
            get_required_password("flickr", "api_key")
