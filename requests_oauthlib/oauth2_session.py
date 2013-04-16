from __future__ import unicode_literals
import requests
from oauthlib.common import generate_token, urldecode
from oauthlib.oauth2 import WebApplicationClient, InsecureTransportError
from oauthlib.oauth2 import TokenExpiredError


class TokenUpdated(Warning):
    def __init__(self, token):
        super(TokenUpdated, self).__init__()
        self.token = token


class OAuth2Session(requests.Session):
    """Versitile OAuth 2 extension to requests.Session.

    Supports any grant type adhering to oauthlib.oauth2.Client spec including
    the four core OAuth 2 grants.

    Can be used to create authorization urls, fetch tokens and access proteced
    resources using the requests.Session interface you are used to.

    oauthlib.oauth2.WebApplicationClient (default), Authorization Code Grant
    oauthlib.oauth2.MobileApplicationClient, Implicit Grant
    oauthlib.oauth2.LegacyApplicationClient, Password Credentials Grant
    oauthlib.oauth2.BackendApplicationClient, Client Credentials Grant

    Note that the only time you will be using Implicit Grant from python is if
    you are driving a user agent able to obtain URL fragments.
    """

    def __init__(self, client_id=None, client=None, auto_refresh_url=None,
            auto_refresh_kwargs=None, scope=None, redirect_uri=None, token=None,
            state=None, state_generator=None, token_updater=None, **kwargs):
        """Construct a new OAuth 2 client session.

        :param client_id: Client id obtained during registration
        :param client: oauthlib.oauth2.Client to be used. Default is
                       WebApplicationClient which is useful for any
                       hosted application but not mobile or desktop.
        :param scope: List of scopes you wish to request access to
        :param redirect_uri: Redirect URI you registered as callback
        :param token: Token dictionary, must include access_token
                      and token_type.
        :param state: State string used to prevent CSRF. This will be given
                      when creating the authorization url and must be supplied
                      when parsing the authorization response.
        :param state_generator: A no argument function used to generate a
                                state string, must be unguessable.
        :auto_refresh_url: Refresh token endpoint URL, must be HTTPS. Supply
                           this if you wish the client to automatically refresh
                           your access tokens.
        :auto_refresh_kwargs: Extra arguments to pass to the refresh token
                              endpoint.
        :token_updater: Method with one argument, token, to be used to update
                        your token databse on automatic token refresh. If not
                        set a TokenUpdated warning will be raised when a token
                        has been refreshed. This warning will carry the token
                        in its token argument.
        :param kwargs: Arguments to pass to the Session constructor.
        """
        super(OAuth2Session, self).__init__(**kwargs)
        self.client_id = client_id or client.client_id
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.token = token or {}
        self.state_generator = state_generator or generate_token
        self.state = state
        self.auto_refresh_url = auto_refresh_url
        self.auto_refresh_kwargs = auto_refresh_kwargs or {}
        self.token_updater = token_updater
        self._client = client or WebApplicationClient(client_id, token=token)
        self._client._populate_attributes(token or {})

    def new_state(self):
        """Generates a state string to be used in authorizations."""
        self.state = self.state_generator()
        return self.state

    def authorization_url(self, url, **kwargs):
        """Form an authorization URL.

        :param url: Authorization endpoint url, must be HTTPS.
        :param kwargs: Extra parameters to include.
        :return: authorization_url, state
        """
        state = self.new_state()
        return self._client.prepare_request_uri(url,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                state=state,
                **kwargs), state

    def fetch_token(self, token_url, code=None, authorization_response=None,
            body='', username=None, password=None, **kwargs):
        """Generic method for fetching an access token from the token endpoint.

        If you are using the MobileApplicationClient you will want to use
        token_from_fragment instead of fetch_token.

        :param token_url: Token endpoint URL, must use HTTPS.
        :param code: Authorization code (used by WebApplicationClients).
        :param authorization_response: Authorization response URL, the callback
                                       URL of the request back to you. Used by
                                       WebApplicationClients instead of code.
        :param body: Optional application/x-www-form-urlencoded body to add the
                     include in the token request. Prefer kwargs over body.
        :param username: Username used by LegacyApplicationClients.
        :param password: Password used by LegacyApplicationClients.
        :param kwargs: Extra parameters to include in the token request.
        :return: A token dict
        """
        if not token_url.startswith('https://'):
            raise InsecureTransportError()

        if not code and authorization_response:
            self._client.parse_request_uri_response(authorization_response,
                    state=self.state)
            code = self._client.code
        body = self._client.prepare_request_body(code=code, body=body,
                redirect_uri=self.redirect_uri, username=username,
                password=password, **kwargs)
        # (ib-lundgren) All known, to me, token requests use POST.
        r = self.post(token_url, data=dict(urldecode(body)))
        self._client.parse_request_body_response(r.content, scope=self.scope)
        self.token = self._client.token
        return self.token

    def token_from_fragment(self, authorization_response):
        """Parse token from the URI fragment, used by MobileApplicationClients.

        :param authorization_response: The full URL of the redirect back to you
        :return: A token dict
        """
        self._client.parse_request_uri_response(authorization_response,
                state=self.state)
        self.token = self._client.token
        return self.token

    def refresh_token(self, token_url, refresh_token=None, body='', **kwargs):
        """Fetch a new access token using a refresh token.

        :param token_url: The token endpoint, must be HTTPS.
        :param refresh_token: The refresh_token to use.
        :param body: Optional application/x-www-form-urlencoded body to add the
                     include in the token request. Prefer kwargs over body.
        :param kwargs: Extra parameters to include in the token request.
        :return: A token dict
        """
        if not token_url:
            raise ValueError('No token endpoint set for auto_refresh.')

        if not token_url.startswith('https://'):
            raise InsecureTransportError()

        # Need to nullify token to prevent it from being added to the request
        refresh_token = refresh_token or self.token.get('refresh_token')
        self.token = {}

        kwargs.update(self.auto_refresh_kwargs)
        body = self._client.prepare_refresh_body(body=body,
                refresh_token=refresh_token, scope=self.scope, **kwargs)
        r = self.post(token_url, data=dict(urldecode(body)))
        self.token = self._client.parse_request_body_response(r.content, scope=self.scope)
        if not 'refresh_token' in self.token:
            self.token['refresh_token'] = refresh_token
        return self.token

    def request(self, method, url, data=None, headers=None, **kwargs):
        """Intercept all requests and add the OAuth 2 token if present."""
        if not url.startswith('https://'):
            raise InsecureTransportError()
        if self.token:
            try:
                url, headers, data = self._client.add_token(url,
                        http_method=method, body=data, headers=headers)
            # Attempt to retrieve and save new access token if expired
            except TokenExpiredError:
                if self.auto_refresh_url:
                    token = self.refresh_token(self.auto_refresh_url)
                    if self.token_updater:
                        self.token_updater(token)
                    else:
                        raise TokenUpdated(token)
                else:
                    raise

        return super(OAuth2Session, self).request(method, url,
                headers=headers, data=data, **kwargs)
