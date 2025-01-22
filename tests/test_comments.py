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
    def test_fixes_mobile_wikipedia_links(self) -> None:
        """
        If there's a mobile Wikipedia link that has disambiguation parens
        at the end, that extra text is added to the URL.
        """
        # This example comes from Barbara Agnew's comment here:
        # https://www.flickr.com/photos/royalaustralianhistoricalsociety/12643854003/#comment72157643236765583
        #
        # Retrieved 22 January 2025
        #
        # Note: we need to preserve both the original scheme (http://)
        # and hostname (en.m.wikipedia.org) because we don't want to
        # be doing any rewriting of people's comments.
        comment_text = '<a href="http://en.m.wikipedia.org/wiki/Black_Thursday_" rel="nofollow">en.m.wikipedia.org/wiki/Black_Thursday_</a>(1851)'
        expected_text = '<a href="http://en.m.wikipedia.org/wiki/Black_Thursday_(1851)" rel="noreferrer nofollow">en.m.wikipedia.org/wiki/Black_Thursday_(1851)</a>'

        assert fix_comment_text(comment_text) == expected_text

    @pytest.mark.vcr()
    def test_fixes_dutch_wikipedia_links(self) -> None:
        """
        If there's a non-English Wikipedia link that has disambiguation parens
        at the end, that extra text is added to the URL.
        """
        # This example comes from Ronald van Ooijen's comment:
        # https://www.flickr.com/photos/statelibraryofnsw/49868448366/#comment72157714245484787
        #
        # Retrieved 22 January 2025
        comment_text = (
            "Ship was until 1934 in use and afterwards scrapped.\n"
            "see for total history\n"
            '<a href="https://nl.wikipedia.org/wiki/Mauretania_" rel="noreferrer nofollow">nl.wikipedia.org/wiki/Mauretania_</a>(schip,_1907)'
        )
        expected_text = (
            "Ship was until 1934 in use and afterwards scrapped.\n"
            "see for total history\n"
            '<a href="https://nl.wikipedia.org/wiki/Mauretania_(schip,_1907)" rel="noreferrer nofollow">nl.wikipedia.org/wiki/Mauretania_(schip,_1907)</a>'
        )

        assert fix_comment_text(comment_text) == expected_text

    @pytest.mark.vcr()
    def test_includes_fragment(self) -> None:
        """
        If there's a Wikipedia URL with a fragment, that fragment is added
        to the URL.
        """
        # This example comes from Jesús Roberto Duarte's comment:
        # https://www.flickr.com/photos/cornelluniversitylibrary/3675113899/#comment72157631107864396
        #
        # Retrieved 22 January 2025
        comment_text = (
            "In\n"
            '<a href="http://es.wikipedia.org/wiki/Atoyac_" rel="nofollow">es.wikipedia.org/wiki/Atoyac_</a>(Veracruz)#Toponimia\n'
            "you'll find its coordinates"
        )
        expected_text = (
            "In\n"
            '<a href="http://es.wikipedia.org/wiki/Atoyac_(Veracruz)#Toponimia" rel="noreferrer nofollow">es.wikipedia.org/wiki/Atoyac_(Veracruz)#Toponimia</a>\n'
            "you'll find its coordinates"
        )

        assert fix_comment_text(comment_text) == expected_text

    @pytest.mark.vcr()
    def test_fixes_wikimedia_commons_link(self) -> None:
        """
        If there's a Wikimedia Commons URL with extra stuff in the suffix,
        that gets added to the URL.
        """
        # This example comes from Peter D. Tillman's comment:
        # https://www.flickr.com/photos/aahs_archives/23586820864/#comment72157667048114519
        #
        # Retrieved 22 January 2025
        comment_text = (
            'In use at <a href="https://en.wikipedia.org/wiki/Bell_YFM-1_Airacuda" rel="nofollow">en.wikipedia.org/wiki/Bell_YFM-1_Airacuda</a>\n'
            "From SDASM, Daniels collection:\n"
            '<a href="https://commons.wikimedia.org/wiki/File:Airacuda_Bell_XFM-1_" rel="nofollow">commons.wikimedia.org/wiki/File:Airacuda_Bell_XFM-1_</a>(15954491367).jpg\n'
            "Thanks for posting these!"
        )
        expected_text = (
            'In use at <a href="https://en.wikipedia.org/wiki/Bell_YFM-1_Airacuda" rel="nofollow">en.wikipedia.org/wiki/Bell_YFM-1_Airacuda</a>\n'
            "From SDASM, Daniels collection:\n"
            '<a href="https://commons.wikimedia.org/wiki/File:Airacuda_Bell_XFM-1_(15954491367).jpg" rel="noreferrer nofollow">commons.wikimedia.org/wiki/File:Airacuda_Bell_XFM-1_(15954491367).jpg</a>\n'
            "Thanks for posting these!"
        )

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

    @pytest.mark.vcr()
    def test_skips_unrecognised_wikipedia(self) -> None:
        """
        A link to a language-specific Wikipedia that doesn't exist
        is skipped.
        """
        comment_text = (
            "This page doesn’t exist: "
            '<a href="https://zz.wikipedia.org/wiki/MadeUpPage" '
            'rel="noreferrer nofollow">zz.wikipedia.org/wiki/MadeUpPage</a>.'
        )

        assert fix_comment_text(comment_text) == comment_text
