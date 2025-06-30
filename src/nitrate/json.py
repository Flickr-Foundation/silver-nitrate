"""
Encode/decode JSON in a type-preserving way.

Our projects use some Python-native types like `datetime`, `date` and `Path`
that don't slot neatly into JSON -- you can store them as strings, but
how do you know you need to convert them back again later?

Our custom encoder/decoder pair store these values as JSON objects with
a `type` key, for example:

    {"type": "datetime.datetime", "value": "2001-02-03T04:05:06"}

This means the intent is clear if you're reading the JSON, but we get
all the nice Python types at both ends.
"""

import datetime
import json
import pathlib
import typing


__all__ = ["NitrateEncoder", "NitrateDecoder"]


T = typing.TypeVar("T")


class NitrateEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that supports datetimes, dates and paths.

        >>> t = datetime.datetime(2001, 2, 3, 4, 5, 6)
        >>> json.dumps({"t": t}, cls=NitrateEncoder)
        '{"t": {"type": "datetime.datetime", "value": "2001-02-03T04:05:06"}}'

    This is meant to be used with ``NitrateDecoder`` -- together, they
    allow you to serialise a datetime value via JSON and preserve its type.

    """

    def default(self, t: T) -> typing.Any:
        """
        Convert a Python value to a JSON value.
        """
        if isinstance(t, datetime.datetime):
            return {"type": "datetime.datetime", "value": t.isoformat()}
        elif isinstance(t, datetime.date):
            return {"type": "datetime.date", "value": t.isoformat()}
        elif isinstance(t, pathlib.Path):
            return {"type": "pathlib.Path", "value": str(t)}
        else:
            return super().default(t)


class NitrateDecoder(json.JSONDecoder):
    """
    A custom JSON decoder that supports the values encoded by
    NitrateEncoder.

        >>> json.loads(
        ...     '{"t": {"type": "datetime.datetime", "value": "2001-02-03T04:05:06"}}',
        ...     cls=NitrateDecoder)
        {'t': datetime.datetime(2001, 2, 3, 4, 5, 6)}

    """

    def __init__(self) -> None:
        """
        Create a new JSONDecoder.

        The ``object_hook`` will be called with the result of any
        object literal that gets decoded.
        """
        super().__init__(object_hook=self.dict_to_object)

    def dict_to_object(self, d: dict[str, typing.Any]) -> typing.Any:
        """
        Convert a JSON value to a Python-native value.
        """
        if d.keys() == {"type", "value"}:
            if d.get("type") == "datetime.datetime":
                return datetime.datetime.fromisoformat(d["value"])
            elif d.get("type") == "datetime.date":
                return datetime.datetime.fromisoformat(d["value"]).date()
            elif d.get("type") == "pathlib.Path":
                return pathlib.Path(d["value"])

        return d
