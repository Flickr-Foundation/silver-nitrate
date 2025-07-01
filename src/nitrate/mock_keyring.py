"""
A pytest fixture that allows you to mock the keyring module.

We use the keyring module in a lot of our code to save and retrieve
passwords from the system keychain. However, we don't want to put real
passwords in our CI environment or tests, i.e. GitHub Actions.

This fixture creates a mock keyring where you can set passwords,
which will then be used by the code under test. Here's an example of
how to use it:

    import keyring
    from keyring.backend import KeyringBackend

    from nitrate.mock_keyring import *  # noqa: F403


    def test_my_code_using_passwords(mock_keyring: KeyringBackend):
        mock_keyring.set_password("flickr_api", "key", "123")

        # call code that uses `keyring.get_password()`

This fixture is completely isolated from your real keychain -- it gets
an empty set of passwords, and the test defines all the passwords
which are available to your code.
"""

from collections.abc import Iterator

import keyring
from keyring.backend import KeyringBackend
import pytest


__all__ = ["mock_keyring"]


@pytest.fixture
def mock_keyring() -> Iterator[KeyringBackend]:
    """
    A pytest fixture that creates an empty, in-memory keyring that is
    used for the duration of a test.
    """

    class InMemoryKeyring(KeyringBackend):
        """
        A keyring implementation which stores passwords in a dictionary.

        This is for testing only.
        """

        def __init__(self) -> None:
            """
            Create an empty keychain.
            """
            self.passwords: dict[tuple[str, str], str] = {}

        @property
        def priority(self) -> int:  # type: ignore
            """
            This is a required property on ``KeyringBackend`` implementations,
            and is used to decide which backend to use.
            """
            # We set a very high priority, so when this backend is used,
            # it will supersede any others.
            return 1_000_000  # pragma: no cover

        def set_password(self, service_name: str, username: str, password: str) -> None:
            """
            Store a password in the keychain.
            """
            self.passwords[(service_name, username)] = password

        def get_password(self, service_name: str, username: str) -> str | None:
            """
            Retrieve a password from the keychain.
            """
            return self.passwords.get((service_name, username))

        def delete_password(
            self, service_name: str, username: str
        ) -> None:  # pragma: no cover
            """
            Remove a password from the keychain.

            This function isn't currently used as part of the tests, but
            we need it to construct an instance of KeyringBackend.
            """
            del self.passwords[(service_name, username)]

    default_backend = keyring.get_keyring()
    tmp_backend = InMemoryKeyring()

    keyring.set_keyring(tmp_backend)
    yield tmp_backend
    keyring.set_keyring(default_backend)
