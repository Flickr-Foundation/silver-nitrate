# CHANGELOG

## v1.1.0 - 2023-12-28

Replace the `InMemoryKeyring` class with a new function `use_in_memory_keyring()`.

This avoids keyring trying to use the in-memory keyring when you import `nitrate.passwords`.

## v1.0.1 - 2023-12-27

Allow passing a custom decoder to `nitrate.types.read_typed_json(…, cls=…)`, similar to the `json.load` method in the standard library.

## v1.0.0 - 2023-12-27

Initial version.
