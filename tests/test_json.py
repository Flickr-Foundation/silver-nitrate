"""
Tests for ``nitrate.json``.
"""

import datetime
import json
import pathlib
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
        datetime.date(2001, 2, 3),
        pathlib.Path("x/y/z"),
    ],
)
def test_can_json_round_trip(value: typing.Any) -> None:
    """
    If you encode JSON with ``NitrateEncoder``, you can decode it
    with ``NitrateDecoder`` and get the same value back.
    """
    json_string = json.dumps(value, cls=NitrateEncoder)
    parsed_json_value = json.loads(json_string, cls=NitrateDecoder)

    assert parsed_json_value == value


@pytest.mark.parametrize(
    ["json_string", "value"],
    [
        (
            '{"type": "datetime.datetime", "value": "2001-02-03T04:05:06"}',
            datetime.datetime(2001, 2, 3, 4, 5, 6),
        ),
        (
            '{"type": "datetime.date", "value": "2001-02-03"}',
            datetime.date(2001, 2, 3),
        ),
        (
            '{"type": "pathlib.Path", "value": "x/y/z"}',
            pathlib.Path("x/y/z"),
        ),
    ],
)
def test_can_decode_json(json_string: str, value: typing.Any) -> None:
    """
    We can decode JSON strings created with ``NitrateEncoder``.

    Note: we use hard-coded strings here to ensure the decoder remains
    compatible across versions, e.g. something encoded with nitrate 1.1
    can be decoded with nitrate 1.2.
    """
    assert json.loads(json_string, cls=NitrateDecoder) == value


def test_encoding_an_unrecognised_type_still_fails() -> None:
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


@pytest.mark.parametrize(
    ["json_string", "value"],
    [
        (
            '{"type": "datetime.date", "string": "2001-01-01"}',
            {"type": "datetime.date", "string": "2001-01-01"},
        ),
        (
            '{"type": "datetime.date", "value": "2001-01-01", "day": "monday"}',
            {"type": "datetime.date", "value": "2001-01-01", "day": "monday"},
        ),
        (
            '{"type": "Currency", "value": "£123.45"}',
            {"type": "Currency", "value": "£123.45"},
        ),
    ],
)
def test_decoding_an_unrecognised_type_is_okay(
    json_string: str, value: typing.Any
) -> None:
    """
    Trying to decode a JSON object which includes a ``type`` key will
    leave it as-is, if it doesn't look like it was encoded by nitrate.
    """
    assert json.loads(json_string, cls=NitrateDecoder) == value
