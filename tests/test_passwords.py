import pytest

from nitrate.passwords import get_required_password, use_in_memory_keyring


class TestGetRequiredPassword:
    def test_gets_existing_password(self) -> None:
        use_in_memory_keyring(initial_passwords={("flickr", "api_key"): "12345"})

        assert get_required_password("flickr", "api_key") == "12345"

    def test_throws_if_password_does_not_exist(self) -> None:
        with pytest.raises(RuntimeError, match="Could not retrieve password"):
            get_required_password("doesnotexist", "doesnotexist")
