"""
Helpers for validating Python types at runtime.

We use a lot of `typing.TypedDict` types to define data structures we're
passing around in our apps, then use the type checker to make sure
we're using them correctly.

The type checker allows us to do static analysis of our code (does this
function return a dict with the right fields?) but it can't check
values received at runtime.  For example, if we read a JSON file from
disk, how do we know it contains data in the right format?

The two functions in this file do this validation for us:

*   `validate_type(value, model=MyCustomType)` checks a Python value,
    and throws a `pydantic.ValidationError` if it doesn't match the type

*   `read_typed_json(path, model=MyCustomType)` reads a value from
    a JSON file, and throws a `pydantic.ValidationError` if it doesn't
    match the type

"""

import functools
import json
from pathlib import Path
import typing

from pydantic import ConfigDict, PydanticUserError, TypeAdapter


__all__ = ["validate_type", "read_typed_json"]


T = typing.TypeVar("T")


@functools.cache
def _get_validator(model: type[T]) -> TypeAdapter[T]:
    """
    Get the validator for a given type.  This is a moderately expensive
    process, so we cache the result -- we only need to create the
    validator once for each type.
    """
    # By default, TypedDict's allow extra keys.
    #
    # You can disable this by setting `extra="forbid"` on the model,
    # either setting it as an attribute directly on the type or
    # passing it to the `TypedAdapter`.
    #
    # We do both:
    #
    #   1.  We try to set the attribute directly on the model.  This is
    #       useful for a model which is a single TypedDict.
    #
    #       It will throw for types which don't support `__pydantic_config__`,
    #       e.g. builtin types.
    #
    #   2.  We try to pass the config to `TypeAdapter` instead.  This is
    #       useful for a Union of TypedDict's, but will throw a UserError
    #       if you try to pass it for a single TypedDict where you can
    #       set the attribute instead.
    #
    # See https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.validate_assignment
    # See https://github.com/pydantic/pydantic/issues/11328#issuecomment-2790046722
    config = ConfigDict(extra="forbid")

    # What is this doing?
    # see https://github.com/pydantic/pydantic/issues/11328#issuecomment-2790046722
    try:
        model.__pydantic_config__ = config  # type: ignore
    except (AttributeError, TypeError):
        pass

    try:
        return TypeAdapter(model, config=config)
    except PydanticUserError:
        return TypeAdapter(model)


def validate_type(t: typing.Any, *, model: type[T]) -> T:
    """
    Check that some data matches a given type.

    We use this to e.g. check that the structured data we receive from
    Wikimedia matches our definitions, so we can use the data in our
    type-checked Python.

    See https://stackoverflow.com/a/77386216/1558022
    """
    # This is to fix an issue from the type checker:
    #
    #     Argument 1 to "__call__" of "_lru_cache_wrapper"
    #     has incompatible type "type[T]"; expected "Hashable"
    #
    assert isinstance(model, typing.Hashable)

    validator = _get_validator(model)

    return validator.validate_python(t, strict=True)


def read_typed_json(
    path: Path | str,
    *,
    model: type[T],
    cls: type[json.JSONDecoder] | None = None,
) -> T:
    """
    Read a JSON file and validate that its contents contain the
    correct type.
    """
    with open(path) as in_file:
        t = json.load(in_file, cls=cls)

    return validate_type(t, model=model)
