"""
Retrieve passwords from the system keychain.

This provides a thin wrapper around the ``keyring`` module.
"""

import keyring


def get_required_password(service_name: str, username: str) -> str:
    """
    Retrieve a password from the keychain, or throw if it's missing.
    """
    # We wrap this API because keyring will return ``None`` rather
    # than tell you a password is missing, e.g.
    #
    #     >>> import keyring
    #     >>> pw = keyring.get_password("doesnotexist", "doesnotexist")
    #     >>> print(pw)
    #     None
    #
    # It's better to throw an error early than let this empty value
    # propagate into our code and bubble up elsewhere.
    #
    # e.g. if we're calling the Flickr API using an API key retrieved
    # using keyring, we'd rather know immediately that it's empty than
    # get a cryptic "invalid API key" error from the Flickr API.
    #
    password = keyring.get_password(service_name, username)

    if password is None:
        raise RuntimeError(f"Could not retrieve password {(service_name, username)}")

    return password


def use_in_memory_keyring(initial_passwords: dict[tuple[str, str], str]) -> None:
    """
    Create an in-memory keyring with a given set of passwords.

    This is useful for testing, when you want to test the interaction
    between a piece of code and the keychain.
    """

    class InMemoryKeyring(keyring.backend.KeyringBackend):
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

    kr = InMemoryKeyring()

    for (service_name, username), password in initial_passwords.items():
        kr.set_password(service_name, username, password)

    keyring.set_keyring(kr)


__all__ = ["get_required_password"]
