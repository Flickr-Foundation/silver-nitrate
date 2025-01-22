"""
Tests for ``nitrate.comments``.
"""

import pytest

from nitrate.comments import fix_comment_text


@pytest.mark.parametrize(
    "comment_text",
    [
        "",
        "Love old gravestones",
        "Text with\na newline",
        'This is a link to <a href="https://example.com" rel="noreferrer nofollow">example.com</a>.',
        'Link to <a href="https://example.com" rel="noreferrer nofollow">example.com</a> in a sentence',
    ],
)
def test_text_is_unchanged(comment_text: str) -> None:
    """
    All of these examples are left unchanged by the comment fixes.
    """
    assert fix_comment_text(comment_text) == comment_text


class TestFixWikipediaLinks:
    """
    Tests for the Wikipedia link fixes.
    """

    @pytest.mark.vcr()
    def test_fixes_trailing_period(self) -> None:
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

        assert fix_comment_text(comment_text) == expected_text

    @pytest.mark.vcr()
    def test_fixes_disambiguation_parens(self) -> None:
        """
        If there's a Wikipedia URL that has disambiguation parens at
        the end, that extra text is identified as part of the URL.
        """
        # This example comes from Jessamyn's comment here:
        # https://www.flickr.com/photos/twm_news/5257092205/#comment72157720409554465
        #
        # Retrieved 21 January 2025
        comment_text = 'This guy! <a href="https://en.wikipedia.org/wiki/Reg_Dixon_" rel="noreferrer nofollow">en.wikipedia.org/wiki/Reg_Dixon_</a>(comedian)'
        expected_text = 'This guy! <a href="https://en.wikipedia.org/wiki/Reg_Dixon_(comedian)" rel="noreferrer nofollow">en.wikipedia.org/wiki/Reg_Dixon_(comedian)</a>'

        assert fix_comment_text(comment_text) == expected_text

    @pytest.mark.vcr()
    def test_skips_correct_link(self) -> None:
        """
        A Wikipedia link that is correct is unchanged.
        """
        comment_text = (
            '<a href="https://en.wikipedia.org/wiki/Flickr" '
            'rel="noreferrer nofollow">en.wikipedia.org/wiki/Flickr</a>.'
        )

        assert fix_comment_text(comment_text) == comment_text

    @pytest.mark.vcr()
    def test_skips_unwanted_trailing_period(self) -> None:
        """
        If the trailing period isn't part of the Wikipedia page title,
        that period isn't added to the URL.
        """
        comment_text = 'You’re thinking of <a href="https://en.wikipedia.org/wiki/Longitude">en.wikipedia.org/wiki/Longitude</a>.'

        assert fix_comment_text(comment_text) == comment_text

    @pytest.mark.vcr()
    def test_skips_ambiguous_url(self) -> None:
        """
        If there's no Wikipedia page with or without the punctuation,
        it leaves the link as-is -- there's no obviously right thing
        for us to do here.
        """
        comment_text = 'This page <a href="https://en.wikipedia.org/wiki/DoesNotExist" rel="noreferrer nofollow">en.wikipedia.org/wiki/DoesNotExist</a>.'

        assert fix_comment_text(comment_text) == comment_text

    @pytest.mark.vcr()
    def test_skips_link_followed_by_whitespace(self) -> None:
        """
        A Wikipedia link followed by whitespace is unchanged.
        """
        comment_text = (
            '<a href="https://en.wikipedia.org/wiki/Flickr" '
            'rel="noreferrer nofollow">en.wikipedia.org/wiki/Flickr</a>\n'
            "That’s it, that’s the whole link."
        )

        assert fix_comment_text(comment_text) == comment_text

    @pytest.mark.vcr()
    def test_skips_homepage_link(self) -> None:
        """
        A link to the Wikipedia homepage is unchanged.
        """
        comment_text = (
            "This is the Wikipedia homepage: "
            '<a href="https://en.wikipedia.org/" '
            'rel="noreferrer nofollow">en.wikipedia.org/</a>.'
        )

        assert fix_comment_text(comment_text) == comment_text
