import contextlib

from vcr.cassette import Cassette

def use_cassette(
    cassette_name: str,
    cassette_library_dir: str,
    decode_compressed_response: bool,
) -> contextlib.AbstractContextManager[Cassette]: ...
