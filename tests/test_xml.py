"""
Tests for ``nitrate.xml``.
"""

import xml.etree.ElementTree as ET

import pytest

from nitrate.xml import find_required_elem, find_required_text, find_optional_text


XML = ET.fromstring(
    """
    <?xml version="1.0" encoding="utf-8" ?>
    <greeting>
        <english>Hello world</english>
        <french/>
        <hungarian></hungarian>
    </greeting>""".strip()
)


def test_find_required_elem() -> None:
    """
    If we look for a required element that exists, we find it.
    """
    english = find_required_elem(XML, path=".//english")
    assert english is not None
    assert english.text == "Hello world"


def test_find_required_elem_throws_if_cannot_find_element() -> None:
    """
    Looking for a required element that doesn't exist
    throws a ``ValueError``.
    """
    with pytest.raises(ValueError, match="Could not find required match"):
        find_required_elem(XML, path=".//german")


def test_find_required_text() -> None:
    """
    If we look for text in a required element that exists, we find it.
    """
    assert find_required_text(XML, path=".//english") == "Hello world"


def test_find_required_text_throws_if_finds_element_without_text() -> None:
    """
    Looking for text in a required element that exists but is empty
    throws a ``ValueError``.
    """
    with pytest.raises(ValueError, match="Could not find required text"):
        find_required_text(XML, path=".//french")


def test_find_required_text_throws_if_cannot_find_element() -> None:
    """
    Looking for text in a required element that doesn't exist
    throws a ``ValueError``.
    """
    with pytest.raises(ValueError, match="Could not find required match"):
        find_required_text(XML, path=".//german")


@pytest.mark.parametrize(
    ["path", "expected"],
    [
        ("english", "Hello world"),
        ("french", None),
        ("german", None),
        ("hungarian", None),
    ],
)
def test_find_optional_text(path: str, expected: str | None) -> None:
    """
    Looking for optional text will find the text if:

    1.  The element exists, and
    2.  It's non-empty

    """
    assert find_optional_text(XML, path=path) == expected
