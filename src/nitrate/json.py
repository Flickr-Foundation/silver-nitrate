"""
Allow encoding/decoding JSON in a type-preserving way.

In particular, these classes allow us to store ``datetime.datetime``
values in JSON and retrieve them as proper datetime objects, rather
than e.g. strings.
"""

import datetime
import json
import typing


T = typing.TypeVar("T")


class NitrateEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that supports datetimes and paths.

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
        else:
            return super().default(t)


class NitrateDecoder(json.JSONDecoder):
    """
    A custom JSON decoder that supports the datetimes encoded
    by NitrateEncoder.

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

    def dict_to_object(
        self, d: dict[str, typing.Any]
    ) -> dict[str, typing.Any] | datetime.datetime:
        """
        Convert a JSON value to a Python-native value.
        """
        if d.get("type") == "datetime.datetime":
            return datetime.datetime.fromisoformat(d["value"])
        else:
            return d


__all__ = ["NitrateEncoder", "NitrateDecoder"]
