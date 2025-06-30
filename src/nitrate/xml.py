"""
Type-safe helpers for finding matching elements/text in an XML document.

== Why do we need this? ==

We use this when we're parsing responses from the Flickr API, and
there are certain elements we know should always be present in responses.

e.g. responses from the flickr.photos.getInfo API should always have
a <title> element, so we could write:

    title = photo_elem.find(".//title")

The type checker thinks this is `Element | None` -- it doesn't know that
the <title> element should always be present.

*   If the API is working correctly and includes <title>, then we have
    to add lots of `assert X is not None` calls around our codebase
    to satisfy the type checker.
*   If the API is working incorrectly and omits <title>, then we get
    a potentially confusing TypeError when we try to do something with
    a value which is unexpectedly None.

Here's how you use this file:

    from nitrate.xml import find_required_elem

    title = find_required_elem(photo_elem, path=".//title")

Our type-safe helpers solve both these problems:

*   If the API is working correctly and includes <title>, then this
    function returns an `ET.Element` and the type checker is happy
    for us to use it as a defined value.
*   If the API is working incorrectly and omits <title>, then this
    function throws a meaningful error message immediately, rather than
    allowing an unexpected None value to propagate.

"""

import xml.etree.ElementTree as ET


__all__ = [
    "find_required_elem",
    "find_required_text",
    "find_optional_text",
]


def find_required_elem(elem: ET.Element, *, path: str) -> ET.Element:
    """
    Find the first subelement matching ``path``, or throw if absent.
    """
    matching_elem = elem.find(path=path)

    if matching_elem is None:
        raise ValueError(f"Could not find required match for {path!r} in {elem!r}")

    return matching_elem


def find_required_text(elem: ET.Element, *, path: str) -> str:
    """
    Find the text of the first element matching ``path``, or throw if absent.

    Here "text" means the inner text of an element.

    Consider this example:

        <photo>
            <id>123456789</id>
            <title></title>
        </photo>

    If we looked up the text in `.//id`, the function returns `123456789`.

    If we looked up the text in `.//title`, the function throws a `ValueError`
    because that element doesn't have any text.

    If we looked up the text in `.//description`, the function throws
    a `ValueError` because that element doesn't exist.
    """
    matching_elem = find_required_elem(elem, path=path)
    text = matching_elem.text

    if text is None:
        raise ValueError(f"Could not find required text in {matching_elem}")

    return text


def find_optional_text(elem: ET.Element, *, path: str) -> str | None:
    """
    Find the text of the first element matching `path`, or return None
    if the element is missing, has no text, or has empty text.

    Consider this example:

        <photo>
            <id>123456789</id>
            <title></title>
        </photo>

    If we looked up the text in `.//id`, the function returns `123456789`.

    If we looked up the text in `.//title`, the function returns `None`
    because the element doesn't have any text.

    If we looked up the text in `.//description`, the function returns `None`
    because that element doesn't exist.
    """
    matching_elem = elem.find(path=path)

    if matching_elem is None:
        return None

    return matching_elem.text or None
