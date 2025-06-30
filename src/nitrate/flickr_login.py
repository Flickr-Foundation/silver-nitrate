"""
Code for dealing with parts of the Flickr OAuth login process that are
the same for every app.

It's meant to be used in the context of a Flask app, and allows some
of the more complicated bits of the Flickr-Login code to be shared
among all our apps.
"""

import typing

from authlib.integrations.httpx_client import OAuth1Client

from .types import validate_type


__all__ = ["FlickrLoginManager", "RequestToken", "AuthorizationResponse", "AccessToken"]


class FlickrLoginManager:
    """
    This class handles the bulk of the complicated logic for the
    Flickr OAuth flow.
    """

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret

    def authorize(
        self,
        callback_url: str,
        permissions: typing.Literal["read", "write", "delete"] = "read",
    ) -> "AuthorizationResponse":
        """
        This is the first step of logging in with Flickr.

        We get a request token from Flickr, and then we redirect the user
        to Flickr.com where they can log in and approve our app.

        To use this, create an authorization endpoint (e.g. ``/authorize``)
        that calls this function.  Return the result directly.

        Parameters:
            login_destination -- the URL where the user should be sent
            after they complete login.

        """
        # Create an OAuth1Client with the Flickr API key and secret
        oauth_client = OAuth1Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            signature_type="QUERY",
        )

        # Step 1: Get a Request Token
        #
        # This will return an OAuth token and secret, in the form:
        #
        #     {'oauth_callback_confirmed': 'true',
        #      'oauth_token': '721…b37',
        #      'oauth_token_secret': '7e2…91a'}
        #
        # See https://www.flickr.com/services/api/auth.oauth.html#request_token
        request_token = oauth_client.fetch_request_token(
            url="https://www.flickr.com/services/oauth/request_token",
            params={"oauth_callback": callback_url},
        )

        # Step 2: Getting the User Authorization
        #
        # This creates an authorization URL on flickr.com, where the user
        # can choose to authorize the app (or not).
        #
        # See https://www.flickr.com/services/api/auth.oauth.html#request_token
        authorization_url = oauth_client.create_authorization_url(
            url=f"https://www.flickr.com/services/oauth/authorize?perms={permissions}"
        )

        # Redirect the user to the Flickr.com URL where they can log in
        # and approve our app.
        return {
            "request_token": validate_type(request_token, model=RequestToken),
            "authorization_url": authorization_url,
        }

    def get_access_token(
        self, authorization_resp_url: str, request_token: "RequestToken"
    ) -> "AccessToken":
        """
        Handle the authorization callback from Flickr.

        After a user approves our app on Flickr.com, they'll be redirected
        back to our app at this URL with some extra parameters, e.g.

            /callback?oauth_token=721…3fd&oauth_verifier=79f…883

        We can use these tokens to get an access token for the user which
        can make Flickr API requests on their behalf.

        This returns an access token you can use to log in the user.
        """
        # Create an OAuth1Client with the Flickr API key and secret.
        #
        # We need to include the request token that we received in the
        # previous step.
        oauth_client = OAuth1Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token=request_token["oauth_token"],
            token_secret=request_token["oauth_token_secret"],
        )

        # Parse the authorization response from Flickr -- that is, extract
        # the OAuth query parameters from the URL, and add them to the client.
        oauth_client.parse_authorization_response(authorization_resp_url)

        # Step 3: Exchanging the Request Token for an Access Token
        #
        # The access token we receive will be of the form:
        #
        #     {'fullname': 'Flickr User',
        #      'oauth_token': '…',
        #      'oauth_token_secret': '…',
        #      'user_nsid': '123456789@N04',
        #      'username': 'flickruser'}
        #
        # See https://www.flickr.com/services/api/auth.oauth.html#access_token
        access_token = oauth_client.fetch_access_token(
            url="https://www.flickr.com/services/oauth/access_token"
        )

        return validate_type(access_token, model=AccessToken)


class RequestToken(typing.TypedDict):
    """
    A request token.  This must be stored after the authorize step,
    and retrieved for the callback step.
    """

    oauth_callback_confirmed: typing.Literal["true"]
    oauth_token: str
    oauth_token_secret: str


class AuthorizationResponse(typing.TypedDict):
    """
    A response to the authorization step.

    This includes the request token (which must be stored for the
    callback step) and the URL where the user must be redirected
    to approve the app.
    """

    request_token: RequestToken
    authorization_url: str


class AccessToken(typing.TypedDict):
    """
    An OAuth access token.  This can be used to make calls to the
    Flickr API.
    """

    fullname: str
    oauth_token: str
    oauth_token_secret: str
    user_nsid: str
    username: str
