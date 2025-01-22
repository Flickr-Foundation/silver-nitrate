"""
Code for dealing with Flickr comments.

In particular, some of Flickr's auto-link detection can be a bit wonky,
e.g. it detects Wikipedia URLs at the wrong point, so we have some code
that fixes it.  This module allows us to apply similar fixes across
all of our projects.

Callers only need one function from this file: ``fix_comment_text``.
"""

from collections.abc import Iterator
import re
import typing
from xml.etree import ElementTree as ET

import httpx
import hyperlink

from .xml import find_required_elem


def fix_comment_text(comment_text: str) -> str:
    """
    Fix broken links and other markup issues in comment text.
    """
    try:
        comment_text = fix_wikipedia_links(comment_text)
    except Exception:
        pass

    return comment_text


class Link(typing.TypedDict):
    """
    Represents an <a> tag found in a block of text.
    """

    raw_markup: str
    href: str
    display_text: str
    suffix: str | None


def find_links(comment_text: str) -> Iterator[Link]:
    """
    Find links in a block of text.

    For this function, we rely on the fact that Flickr auto-links in
    a very particular way, for example:

        <a href="https://example.com" rel="noreferrer nofollow">example.com</a>

    It might be safer to use a proper parser like BeautifulSoup,
    but a Flickr comment isn't a complete HTML document and using
    regex makes it easier to do minimally invasive replacements.

    Note: some older comments omit the ``noreferrer`` attribute.

    """
    # This regex is designed to match all <a> tags in the form above,
    # then capture everything after that up to the next bit of whitespace.
    for m in re.finditer(
        r'<a href="(?P<href>[^"]+)" '
        r'rel="(?:noreferrer )?nofollow">'
        r"(?P<display_text>[^<]+)"
        r"</a>"
        r"(?P<suffix>[^\s]*)",
        comment_text,
    ):
        yield {
            "raw_markup": m.group(0),
            "href": m.group("href"),
            "display_text": m.group("display_text"),
            "suffix": m.group("suffix") or None,
        }


def fix_wikipedia_links(comment_text: str) -> str:
    """
    Fix Wikipedia links in Flickr comments.

    Flickr's comment parser will try to auto-detect links, and it assumes
    punctuation isn't part of links, but this breaks links to some
    Wikipedia pages, for example:

        https://en.wikipedia.org/wiki/William_Barnes_Jr.

    It will omit the final period from the link, which means it goes to
    the wrong page.

    This is a particular issue for Flickr Commons, where people leave
    a lot of comments linking to Wikipedia pages.

    This function will fix the Wikipedia links auto-detected by Flickr.
    It moves any trailing punctuation that's part of the link inside
    the <a>.  We should never change the text of the comment, just move
    bits in/out of the <a>.

    See https://github.com/Flickr-Foundation/commons.flickr.org/issues/297
    """
    for link in find_links(comment_text):
        # If this link is immediately followed by whitespace, we can be
        # confident we've got the full link.
        if link["suffix"] is None:
            continue

        # Parse the URL and get the title of the page
        #
        # We're looking for a URL of the form
        #
        #     https://en.wikipedia.org/wiki/{title}
        #
        # Anything else we should skip.
        url = hyperlink.parse(link["href"])

        is_english_wikipedia = url.host in {
            "en.wikipedia.org",
            "en.m.wikipedia.org",
            "commons.wikimedia.org",
        }

        # It's easier to write a regex than enumerate all of these.
        # e.g. de.wikipedia.org, fr.wikipedia.org
        is_other_wikipedia = re.match(r"^[a-z]{2}\.wikipedia.org$", url.host)

        if not is_english_wikipedia and not is_other_wikipedia:
            continue

        if len(url.path) < 2 or url.path[0] != "wiki":
            continue

        orig_title = url.path[1]

        # If there's a Wikipedia page with this exact title, then the
        # link works and we can leave it as-is.
        if _get_wikipedia_page(host=url.host, title=orig_title) == "found":
            continue

        # Otherwise, check to see if there's a page with the suffix
        # added -- and if there does, use that as the new link.
        #
        # We don't include the fragment when looking up the title of
        # the page, but we do add it if we're fixing the URL.
        if "#" in link["suffix"]:
            suffix, fragment = link["suffix"].split("#")
            fragment = f"#{fragment}"
        else:
            suffix = link["suffix"]
            fragment = ""

        alt_title = orig_title + suffix

        if _get_wikipedia_page(host=url.host, title=alt_title) == "found":
            new_url = f"{url.host}/wiki/{alt_title}{fragment}"

            comment_text = comment_text.replace(
                link["raw_markup"],
                (
                    f'<a href="{url.scheme}://{new_url}" '
                    'rel="noreferrer nofollow">'
                    f"{new_url}</a>"
                ),
            )

    return comment_text


WikipediaPageStatus = typing.Literal["found", "redirected", "not_found"]


def _get_wikipedia_page(host: str, title: str) -> WikipediaPageStatus:
    """
    Look up a page on Wikipedia and see whether it:

    1.  Exists, with the given title
    2.  Exists, but the title is normalized/redirected
    3.  Isn't found

    """
    if host == "en.m.wikipedia.org":
        host = "en.wikipedia.org"

    resp = httpx.get(
        f"https://{host}/w/api.php",
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

    # If the <page> element has the ``missing`` attribute, then there's
    # no such page.
    page = find_required_elem(xml, path=".//page")

    if "missing" in page.attrib:
        return "not_found"

    # If the <page> element has the exact same title as the thing we
    # searched for, then it exists.
    #
    # (Note: Wikipedia replaces spaces with underscores in URLs, which
    # we undo to compare titles.)
    if page.attrib["title"] == title.replace("_", " "):
        return "found"

    # If we found a <page> element but it doesn't have the expected title,
    # we may have been redirected.
    if xml.find(".//normalized") is not None:
        return "redirected"

    # This should never happen in practice so we can't test it, but we
    # include it for the sake of easy debugging if it does.
    else:  # pragma: no cover
        raise RuntimeError(
            f"Unable to parse Wikipedia API response for {title!r}: {resp.text}"
        )
