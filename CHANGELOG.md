# CHANGELOG

## 1.8.0 - 2025-07-01

Replace `nitrate.passwords` with `nitrate.mock_keyring`, a pytest fixture which is a bit clearer and better documented.

This also allows you to define passwords in multiple places, if you're combining other pytest fixtures.

## 1.7.1 - 2025-07-01

Remove `nitrate.passwords.get_required_password`, which was only ever used in one project, and inline it back into that project.

## v1.7.0 - 2025-06-30

Remove `nitrate.comments`, which was only ever used in one project, and inline it back into that project.

## v1.6.2 - 2025-04-14

Fix a bug in the validation of `typing.Union[A, B]` where both types are a `TypedDict`.

The validation is stricter, and will require an exact match to either `A` or `B` -- previously it was possible for data to validate that was only a "partial" match, and this could cause data to be lost.
This was only possible in cases where the fields of `A` were a strict subset of the fields of `B`, and you passed a value which used more fields than `A` but less than `B`.

For example, consider the following type:

```python
BasicShape = typing.TypedDict("Shape", {"sides": int, })
NamedShape = typing.TypedDict("Shape", {"sides": int, "colour": str, "name": str })

Shape = BasicShape | NamedShape
```

if you passed the data:

```python
{"sides": "5", "colour": "red"};
```

this isn't a strict match for `BasicShape` or `NamedShape`, but would be incorrectly validated and returned as `{'sides': 5}`.

Now this throws a `pydantic.ValidationError`.

## v1.6.1 - 2025-03-03

Tidy up the new `FlickrLoginManager.handle_callback` API, which was taking a `login_destination` parameter that it didn't need.

## v1.6.0 - 2025-02-28

This releases adds `nitrate.flickr_login`, which has a `FlickrLoginManager` class that can be used to handle part of the Flickr login process.

This is to reduce the amount of login-related code we need to share between our different apps.
It doesn't remove it completely, but the code that actually talks to Flickr now lives in this library.

This will likely be refined as we work out what the right amount of code to share/reuse is.

## v1.5.0 - 2025-02-28

This release includes packaging extras, so you can declare the specific parts of `silver-nitrate` that you want, and it will include their dependencies.

For example, you could install `silver-nitrate[types]`, and that will install Pydantic, rather than you having to specify Pydantic as a separate dependency.

## v1.4.0 - 2025-02-05

This replaces `nitrate.json.DatetimeEncoder` with `nitrate.json.NitrateEncoder` (and similar for `Decoder`).

This new encoder/decoder pair is backwards-compatible with JSON written by previous versions of silver-nitrate, but now can decode/encode more types:

-   `datetime.datetime`
-   `datetime.date`
-   `pathlib.Path`

## v1.3.0 - 2025-01-22

Change `nitrate.comments` to provide a more generic function `fix_comment_text`.
Currently this just does the Wikipedia link fixing from v1.2.0, but we may add more features in future.

This also improves the Wikipedia link fixing, to include fixing:

*   Links to Wikipedia mobile and non-English Wikipedias
*   Links to Wikimedia Commons
*   URL fragments/anchors

## v1.2.0 - 2025-01-21

Add a new module `nitrate.comments` which contains a single function `fix_wikipedia_links`.

This is for fixing the auto-detected links in Flickr comments, where Wikipedia URLs are often detected incorrectly.

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
