import typing

import httpx

class RequestTokenResp(typing.TypedDict):
    oauth_token: str

class ParseAuthorizationResponse(typing.TypedDict):
    user_nsid: str

class OAuth1Client(httpx.Client):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        signature_type: typing.Literal["QUERY"] | None = None,
        token: str | None = None,
        token_secret: str | None = None,
    ) -> None: ...
    def fetch_request_token(
        self, url: str, params: dict[str, str]
    ) -> RequestTokenResp: ...
    def create_authorization_url(
        self, url: str, request_token: str | None = None
    ) -> str: ...
    def fetch_access_token(
        self, url: str, verifier: str | None = None
    ) -> typing.Any: ...
    token: typing.Any
    def parse_authorization_response(self, url: str) -> ParseAuthorizationResponse: ...
