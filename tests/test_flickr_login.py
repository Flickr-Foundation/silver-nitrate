"""
Tests for ``nitrate.flickr_login``.
"""

from collections.abc import Iterator
import os

import pytest
import vcr
from vcr.cassette import Cassette

from nitrate.flickr_login import FlickrLoginManager


@pytest.fixture
def login_manager() -> FlickrLoginManager:
    """
    Creates a basic login manager.  You can pass real OAuth credentials
    as environment variables, or it just uses dummy values.
    """
    client_id = os.environ.get("CLIENT_ID", "123")
    client_secret = os.environ.get("CLIENT_SECRET", "456")

    return FlickrLoginManager(client_id=client_id, client_secret=client_secret)


@pytest.fixture
def flickr_oauth_cassette(cassette_name: str) -> Iterator[Cassette]:
    """
    Create a vcrpy cassette that records HTTP interactions, so they
    can be replayed later.  This allows you to run the test suite
    without having any OAuth credentials (e.g. in GitHub Actions).

    This cassette will redact any OAuth-related parameters from
    requests and responses.  This ensures that we don't commit
    any real credentials to the test fixtures.
    """
    with vcr.use_cassette(
        cassette_name,
        cassette_library_dir="tests/fixtures/cassettes",
        filter_query_parameters=[
            ("oauth_consumer_key", "OAUTH_CONSUMER_KEY"),
            ("oauth_nonce", "OAUTH_NONCE"),
            ("oauth_signature", "OAUTH_SIGNATURE"),
            ("oauth_timestamp", "OAUTH_TIMESTAMP"),
            ("oauth_verifier", "OAUTH_VERIFIER"),
        ],
        filter_headers=[("authorization", "AUTHORIZATION")],
        decode_compressed_response=True,
    ) as cassette:
        yield cassette


def test_complete_login_flow(
    flickr_oauth_cassette: Cassette,
    login_manager: FlickrLoginManager,
) -> None:
    """
    This is an end-to-end test of our login flow.

    I had to use real OAuth credentials to set up this test.

    What I did:

    1.  Ran the first half of the test, up to the commented-out ``assert 0``.
        This gave me a real authorization URL I could open in Flickr.

    2.  I clicked that authorization URL, which took me to a localhost/…
        URL.  I pasted that into the callback_resp line.

    3.  I ran the entire test, with the ``assert 0`` commented out.  This did
        the token exchange with Flickr.

    4.  I redacted the secrets from the URL and the VCR cassette.

    """
    authorize_resp = login_manager.authorize(
        callback_url="http://localhost/callback", permissions="read"
    )

    print(authorize_resp)
    assert authorize_resp == {
        "request_token": {
            "oauth_callback_confirmed": "true",
            "oauth_token": "REQUEST_TOKEN",
            "oauth_token_secret": "REQUEST_TOKEN_SECRET",
        },
        "authorization_url": "https://www.flickr.com/services/oauth/authorize?perms=read&oauth_token=REQUEST_TOKEN",
    }
    # assert 0

    access_token = login_manager.get_access_token(
        authorization_resp_url="http://localhost/callback?oauth_token=OAUTH_TOKEN&oauth_verifier=OAUTH_VERIFIER",
        request_token=authorize_resp["request_token"],
    )

    assert access_token == {
        "fullname": "Alex Chan",
        "oauth_token": "ACCESS_TOKEN",
        "oauth_token_secret": "ACCESS_TOKEN_SECRET",
        "user_nsid": "199258389@N04",
        "username": "alexwlchan",
    }
