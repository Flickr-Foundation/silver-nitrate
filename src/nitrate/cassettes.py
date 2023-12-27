"""
Use cassettes for testing HTTP APIs with VCR.py [1]

This establishes a couple of conventions for where cassettes are stored
and how they're named.

[1]: https://vcrpy.readthedocs.io/
"""

from collections.abc import Generator

import pytest
import vcr
from vcr.cassette import Cassette


def get_cassette_name(request: pytest.FixtureRequest) -> str:
    """
    Returns the name of a cassette for vcr.py.

    The name can be made up of (up to) three parts:

    -   the name of the test class
    -   the name of the test function
    -   the ID of the test case in @pytest.mark.parametrize

    """
    name = request.node.name

    # This is to catch cases where e.g. we try to include a complete
    # HTTP URL in a cassette name, which creates very messy folders in
    # the fixtures directory.
    if any(char in name for char in ":/."):
        raise ValueError(
            "Illegal characters in VCR cassette name - "
            "please set a test ID with @pytest.param(…, id='…')"
        )

    if request.cls is not None:
        return f"{request.cls.__name__}.{name}.yml"
    else:
        return f"{name}.yml"


@pytest.fixture(scope="function")
def cassette_name(request: pytest.FixtureRequest) -> str:
    return get_cassette_name(request)


@pytest.fixture(scope="function")
def vcr_cassette(cassette_name: str) -> Generator[Cassette, None, None]:
    """
    Creates a VCR cassette for use in tests.

    Anything using httpx in this test will record its HTTP interactions
    as "cassettes" using vcr.py, which can be replayed offline
    (e.g. in CI tests).
    """
    with vcr.use_cassette(
        cassette_name,
        cassette_library_dir="tests/fixtures/cassettes",
    ) as cassette:
        yield cassette


__all__ = ["cassette_name", "vcr_cassette"]
