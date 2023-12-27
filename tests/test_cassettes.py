import httpx
import pytest
from vcr.cassette import Cassette

from nitrate.cassettes import get_cassette_name


def test_creates_cassette(cassette_name: str) -> None:
    assert cassette_name == "test_creates_cassette.yml"


@pytest.mark.parametrize(
    ["expected_cassette_name"],
    [
        pytest.param("test_creates_parametrized_cassette[test1].yml", id="test1"),
        pytest.param("test_creates_parametrized_cassette[test2].yml", id="test2"),
        pytest.param("test_creates_parametrized_cassette[test3].yml", id="test3"),
    ],
)
def test_creates_parametrized_cassette(
    cassette_name: str, expected_cassette_name: str
) -> None:
    assert cassette_name == expected_cassette_name


class TestCassetteNameInClass:
    def test_prefixes_class_name_to_cassette(self, cassette_name: str) -> None:
        assert (
            cassette_name
            == "TestCassetteNameInClass.test_prefixes_class_name_to_cassette.yml"
        )

    @pytest.mark.parametrize(
        ["expected_cassette_name"],
        [
            pytest.param(
                "TestCassetteNameInClass.test_prefixes_name_with_parametrized_cassette[test1].yml",
                id="test1",
            ),
            pytest.param(
                "TestCassetteNameInClass.test_prefixes_name_with_parametrized_cassette[test2].yml",
                id="test2",
            ),
            pytest.param(
                "TestCassetteNameInClass.test_prefixes_name_with_parametrized_cassette[test3].yml",
                id="test3",
            ),
        ],
    )
    def test_prefixes_name_with_parametrized_cassette(
        self, cassette_name: str, expected_cassette_name: str
    ) -> None:
        assert cassette_name == expected_cassette_name


@pytest.mark.parametrize("url", ["https://example.com"])
def test_throws_if_bad_cassette_name(url: str, request: pytest.FixtureRequest) -> None:
    with pytest.raises(ValueError, match="Illegal characters in VCR cassette name"):
        get_cassette_name(request)


def test_creates_cassette_in_fixture_dir(vcr_cassette: Cassette) -> None:
    resp = httpx.get("https://example.com")
    resp.raise_for_status()

    assert (
        vcr_cassette._path
        == "tests/fixtures/cassettes/test_creates_cassette_in_fixture_dir.yml"
    )
