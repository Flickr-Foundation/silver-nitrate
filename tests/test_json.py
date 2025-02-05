"""
Tests for ``nitrate.json``.
"""

import datetime
import json
import typing
import uuid

import pytest

from nitrate.json import NitrateDecoder, NitrateEncoder


@pytest.mark.parametrize(
    "value",
    [
        "an interesting time",
        1234,
        None,
        ["1", "2", "3"],
        {"sides": 5, "color": "red"},
        datetime.datetime(2001, 2, 3, 4, 5, 6),
    ],
)
def test_can_json_round_trip(value: typing.Any) -> None:
    """
    If you encode JSON with ``NitrateEncoder``, you can decode it
    with ``NitrateDecoder`` and get the same value back.
    """
    json_string = json.dumps(value, cls=NitrateEncoder)
    parsed_json_string = json.loads(json_string, cls=NitrateDecoder)

    assert parsed_json_string == value


def test_an_unrecognised_type_still_fails() -> None:
    """
    Trying to encode an unrecognised type will fail, even if you use
    ``NitrateEncoder``.

    This is a regression test for an old bug where ``NitrateEncoder``
    would silently drop values with unrecognised types.
    """
    with pytest.raises(TypeError, match="Object of type UUID is not JSON serializable"):
        json.dumps({"id": uuid.uuid4()})

    with pytest.raises(TypeError, match="Object of type UUID is not JSON serializable"):
        json.dumps({"id": uuid.uuid4()}, cls=NitrateEncoder)
