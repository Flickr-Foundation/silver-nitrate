"""
Tests for ``nitrate.types``.
"""

import datetime
from pathlib import Path
import typing

import pytest
from pydantic import ValidationError

from nitrate.json import NitrateDecoder
from nitrate.types import read_typed_json, validate_type


Shape = typing.TypedDict("Shape", {"color": str, "sides": int})
Circle = typing.TypedDict("Circle", {"color": str, "radius": int})


@pytest.mark.parametrize(
    "data",
    [
        {"color": "red"},
        {"sides": 4},
        {"color": "red", "sides": "four"},
        {"color": (255, 0, 0), "sides": 4},
        {"color": "red", "sides": 4, "angle": 36},
    ],
)
def test_validate_type_flags_incorrect_data(data: typing.Any) -> None:
    """
    If you pass data that doesn't match the model to ``validate_type``,
    it throws a ``ValidationError``.
    """
    with pytest.raises(ValidationError):
        validate_type(data, model=Shape)


def test_validate_type_allows_valid_data() -> None:
    """
    If you pass data which matches the model to ``validate_type``,
    it passes without exception.
    """
    validate_type({"color": "red", "sides": 4}, model=Shape)


def test_validate_type_supports_builtin_list() -> None:
    """
    You can validate a list with ``validate_type``.
    """
    validate_type([1, 2, 3], model=list[int])


def test_validate_type_supports_builtin_type() -> None:
    """
    You can validate a list with ``validate_type``.
    """
    validate_type(1, model=int)


@pytest.mark.parametrize(
    "data", [{"color": "red", "sides": 4}, {"color": "blue", "radius": 3}]
)
def test_validate_type_supports_union_type(data: typing.Any) -> None:
    """
    You can validate a type which is a union of two TypedDict's.
    """
    validate_type(data, model=Shape | Circle)  # type: ignore


@pytest.mark.parametrize(
    "data",
    [
        {"color": "red", "sides": 4, "name": "square"},
        {"color": "red", "sides": 4, "stroke": "black", "depth": 3},
    ],
)
def test_validate_type_rejects_extra_fields(data: typing.Any) -> None:
    """
    Adding extra keys to a TypedDict is a validation error.
    """
    with pytest.raises(ValidationError):
        validate_type(data, model=Shape)


@pytest.mark.parametrize(
    "data",
    [
        {"color": "red", "sides": 4, "name": "square"},
        {"color": "red", "sides": 4, "stroke": "black", "depth": 3},
    ],
)
def test_validate_type_of_union_rejects_extra_fields(data: typing.Any) -> None:
    """
    Adding extra keys to a Union of TypedDict's is a validation error.
    """
    with pytest.raises(ValidationError):
        validate_type(data, model=Shape | Circle)  # type: ignore


def test_read_typed_json_allows_valid_data(tmp_path: Path) -> None:
    """
    If you read a JSON file which matches the model with ``read_typed_json``,
    it returns the data.
    """
    json_path = tmp_path / "data.json"

    with open(json_path, "w") as out_file:
        out_file.write("[1, 2, 3]")

    assert read_typed_json(json_path, model=list[int]) == [1, 2, 3]


def test_read_typed_json_flags_invalid_data(tmp_path: Path) -> None:
    """
    If you read a JSON file which doesn't match the model with
    ``read_typed_json``, it throws a ``ValidationError``.
    """
    json_path = tmp_path / "data.json"

    with open(json_path, "w") as out_file:
        out_file.write("[1, 2, 3]")

    with pytest.raises(ValidationError):
        read_typed_json(json_path, model=dict[str, str])


def test_read_typed_json_uses_decoder(tmp_path: Path) -> None:
    """
    If you pass a custom decoder to ``read_typed_json``, it will use that
    to decode the JSON before validating it against the model.
    """
    json_path = tmp_path / "data.json"

    with open(json_path, "w") as out_file:
        out_file.write(
            '{"date": {"type": "datetime.datetime", "value": "2023-12-27T14:16:02Z"}}'
        )

    with pytest.raises(ValidationError):
        read_typed_json(json_path, model=dict[str, datetime.datetime])

    expected = {
        "date": datetime.datetime(2023, 12, 27, 14, 16, 2, tzinfo=datetime.timezone.utc)
    }

    actual = read_typed_json(
        json_path, model=dict[str, datetime.datetime], cls=NitrateDecoder
    )

    assert actual == expected
