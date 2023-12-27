import datetime
import json

from nitrate.json import DatetimeDecoder, DatetimeEncoder


def test_can_json_round_trip() -> None:
    d = {
        "label": "an interesting time",
        "time": datetime.datetime(2001, 2, 3, 4, 5, 6),
    }

    json_string = json.dumps(d, cls=DatetimeEncoder)
    parsed_json_string = json.loads(json_string, cls=DatetimeDecoder)

    assert parsed_json_string == d
