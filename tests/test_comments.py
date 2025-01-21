"""
Tests for ``nitrate.comments``.
"""

import pytest

from nitrate.comments import fix_wikipedia_links


class TestFixWikipediaLinks:
    """
    Tests for ``fix_wikipedia_links``.
    """

    @pytest.mark.parametrize(
        "comment_text",
        [
            "",
            "Love old gravestones",
            "Text with\na newline",
            'This is a link to <a href="https://example.com">example.com</a>.',
        ],
    )
    def test_text_is_unchanged(self, comment_text: str) -> None:
        """
        If a comment doesn't contain any Wikipedia links, then it's
        unchanged by the Wikipedia link fixer.
        """
        assert fix_wikipedia_links(comment_text) == comment_text

    @pytest.mark.vcr()
    def test_correct_wikipedia_link_is_unchanged(self) -> None:
        """
        A Wikipedia link that is correct is left unchanged.
        """
        comment_text = (
            '<a href="https://en.wikipedia.org/wiki/Flickr" '
            'rel="noreferrer nofollow">en.wikipedia.org/wiki/Flickr</a>.'
        )

        assert fix_wikipedia_links(comment_text) == comment_text

    @pytest.mark.vcr()
    def test_it_fixes_trailing_period(self) -> None:
        """
        If there's a Wikipedia URL that ends with a period, that period
        is correctly identified as part of the URL.

        See https://github.com/Flickr-Foundation/commons.flickr.org/issues/297
        """
        comment_text = (
            '<a href="https://en.wikipedia.org/wiki/William_Barnes_Jr" '
            'rel="noreferrer nofollow">en.wikipedia.org/wiki/William_Barnes_Jr</a>.'
        )
        expected_text = (
            '<a href="https://en.wikipedia.org/wiki/William_Barnes_Jr." '
            'rel="noreferrer nofollow">en.wikipedia.org/wiki/William_Barnes_Jr.</a>'
        )

        assert fix_wikipedia_links(comment_text) == expected_text
