import contextlib

from .cassette import Cassette

def use_cassette(
    cassette_name: str,
    cassette_library_dir: str,
) -> contextlib.AbstractContextManager[Cassette]: ...
