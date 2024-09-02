"""
Tests for ``nitrate.json``.
"""

import datetime
import json
import uuid

import pytest

from nitrate.json import DatetimeDecoder, DatetimeEncoder


def test_can_json_round_trip() -> None:
    """
    If you encode JSON with ``DatetimeEncoder``, you can decode it
    with ``DatetimeDecoder`` and get the same value back.
    """
    d = {
        "label": "an interesting time",
        "time": datetime.datetime(2001, 2, 3, 4, 5, 6),
    }

    json_string = json.dumps(d, cls=DatetimeEncoder)
    parsed_json_string = json.loads(json_string, cls=DatetimeDecoder)

    assert parsed_json_string == d


def test_an_unrecognised_type_still_fails() -> None:
    """
    Trying to encode an unrecognised type will fail, even if you use
    ``DatetimeEncoder``.

    This is a regression test for an old bug where ``DatetimeEncoder``
    would silently drop values with unrecognised types.
    """
    with pytest.raises(TypeError, match="Object of type UUID is not JSON serializable"):
        json.dumps({"id": uuid.uuid4()})

    with pytest.raises(TypeError, match="Object of type UUID is not JSON serializable"):
        json.dumps({"id": uuid.uuid4()}, cls=DatetimeEncoder)
