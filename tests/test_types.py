import pathlib
from typing import Any, TypedDict

import pytest
from pydantic import ValidationError

from nitrate.types import read_typed_json, validate_type


class Shape(TypedDict):
    color: str
    sides: int


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
def test_validate_type_flags_incorrect_data(data: Any) -> None:
    with pytest.raises(ValidationError):
        validate_type(data, model=Shape)


def test_validate_type_allows_valid_data() -> None:
    validate_type({"color": "red", "sides": 4}, model=Shape)


def test_validate_type_supports_builtin_types() -> None:
    validate_type([1, 2, 3], model=list[int])


def test_read_typed_json_allows_valid_data(tmp_path: pathlib.Path) -> None:
    json_path = tmp_path / "data.json"

    with open(json_path, "w") as out_file:
        out_file.write("[1, 2, 3]")

    assert read_typed_json(json_path, model=list[int]) == [1, 2, 3]


def test_read_typed_json_flags_invalid_data(tmp_path: pathlib.Path) -> None:
    json_path = tmp_path / "data.json"

    with open(json_path, "w") as out_file:
        out_file.write("[1, 2, 3]")

    with pytest.raises(ValidationError):
        read_typed_json(json_path, model=dict[str, str])
