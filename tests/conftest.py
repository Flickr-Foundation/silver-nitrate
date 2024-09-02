"""
Re-export the VCR cassette fixtures so they're available to this test suite.
"""

from nitrate.cassettes import cassette_name, vcr_cassette

__all__ = ["cassette_name", "vcr_cassette"]
