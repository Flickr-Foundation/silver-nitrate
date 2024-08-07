# CHANGELOG

## v1.1.3 - 2024-08-09

VCR cassettes recorded with the `vcr_cassette` fixture will now store responses as plain text strings, not binary-encoded data.

## v1.1.2 - 2024-07-15

Allow periods in the names of VCR cassettes created by `nitrate.cassettes`.

## v1.1.1 - 2024-06-06

Fix a bug with the JSON encoder where throw a `ValueError: Circular reference detected` error for types which can't be encoded.

## v1.1.0 - 2023-12-28

Replace the `InMemoryKeyring` class with a new function `use_in_memory_keyring()`.

This avoids keyring trying to use the in-memory keyring when you import `nitrate.passwords`.

## v1.0.1 - 2023-12-27

Allow passing a custom decoder to `nitrate.types.read_typed_json(…, cls=…)`, similar to the `json.load` method in the standard library.

## v1.0.0 - 2023-12-27

Initial version.
