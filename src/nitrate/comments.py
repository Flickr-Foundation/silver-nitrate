"""
Code for dealing with Flickr comments.

In particular, it has some code shared across our
"""

import re
from xml.etree import ElementTree as ET

import httpx

from .xml import find_required_elem


def fix_wikipedia_links(comment_text: str) -> str:
    """
    Fix Wikipedia links in Flickr comments.

    Flickr's comment parser will try to auto-detect links, and it assumes
    punctuation isn't part of links, but this breaks links to some
    Wikipedia pages, for example:

        https://en.wikipedia.org/wiki/William_Barnes_Jr.

    It will omit the final period from the link, which means it goes to
    the wrong page.

    This function will fix the Wikipedia links auto-detected by Flickr.
    It moves any trailing punctuation that's part of the link inside
    the <a>.  We aren't changing the text of the comment, just the
    auto-detected HTML markup.

    See https://github.com/Flickr-Foundation/commons.flickr.org/issues/297
    """
    for m in re.finditer(
        r'<a href="https://en\.wikipedia\.org/wiki/(?P<slug1>[A-Za-z_]+)"'
        r' rel="noreferrer nofollow">'
        r"en\.wikipedia\.org/wiki/(?P<slug2>[A-Za-z_]+)"
        r"</a>"
        r"\.",
        comment_text,
    ):
        # This is a defensive measure, because it was easier than
        # getting lookback groups working in the regex.
        if m.group("slug1") != m.group("slug2"):  # pragma: no cover
            continue

        title = m.group("slug1")

        # if does_wikipedia_page_exist()

        if not does_wikipedia_page_exist(title) and does_wikipedia_page_exist(
            title + "."
        ):
            new_title = title + "."

            comment_text = comment_text.replace(
                m.group(0),
                (
                    f'<a href="https://en.wikipedia.org/wiki/{new_title}" '
                    'rel="noreferrer nofollow">'
                    f"en.wikipedia.org/wiki/{new_title}</a>"
                ),
            )

    return comment_text


def does_wikipedia_page_exist(title: str) -> bool:
    """
    Does a page with this title exist on Wikipedia?
    """
    resp = httpx.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvprop": "timestamp",
            "format": "xml",
        },
    )
    resp.raise_for_status()

    # Note: the ElementTree API is not hardened against untrusted XML,
    # but we trust the Wikipedia API enough to try this.
    xml = ET.fromstring(resp.text)

    # The API response will contain a single ``page`` element,
    # like so:
    #
    #    <?xml version="1.0"?>
    #    <api batchcomplete="">
    #      <query>
    #        <normalized>
    #          <n from="William_Barnes_Jr" to="William Barnes Jr"/>
    #        </normalized>
    #        <pages>
    #          <page _idx="-1" ns="0" title="William Barnes Jr" missing=""/>
    #        </pages>
    #      </query>
    #    </api>
    #
    # If it has the ``missing`` attribute, then there's no such page.
    page = find_required_elem(xml, path=".//page")

    return "missing" not in page.attrib
