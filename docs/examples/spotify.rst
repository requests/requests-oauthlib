Spotify OAuth 2 Tutorial
==========================

Setup a new app in the `Spotify Developer Console`_.
When you have obtained a ``client_id``, ``client_secret`` and registered
a Redirect URI, then you can try out the command line interactive example below.

.. _`Spotify Developer Console`: https://developer.spotify.com/dashboard/applications

.. code-block:: pycon

    >>> # Credentials you get from registering a new application
    >>> client_id = '<the id you get from spotify developer console>'
    >>> client_secret = '<the secret you get from spotify developer console>'
    >>> redirect_uri = 'https://your.registered/callback'

    >>> # OAuth endpoints given in the Spotify API documentation
    >>> # https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
    >>> authorization_base_url = "https://accounts.spotify.com/authorize"
    >>> token_url = "https://accounts.spotify.com/api/token"
    >>> # https://developer.spotify.com/documentation/general/guides/authorization/scopes/
    >>> scope = [
    ...     "user-read-email",
    ...     "playlist-read-collaborative"
    ... ]

    >>> from requests_oauthlib import OAuth2Session
    >>> spotify = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

    >>> # Redirect user to Spotify for authorization
    >>> authorization_url, state = spotify.authorization_url(authorization_base_url)
    >>> print('Please go here and authorize: ', authorization_url)

    >>> # Get the authorization verifier code from the callback url
    >>> redirect_response = input('\n\nPaste the full redirect URL here: ')
    
    >>> from requests.auth import HTTPBasicAuth

    >>> auth = HTTPBasicAuth(client_id, client_secret)

    >>> # Fetch the access token
    >>> token = spotify.fetch_token(token_url, auth=auth,
    ...         authorization_response=redirect_response)
    
    >>> print(token)

    >>> # Fetch a protected resource, i.e. user profile
    >>> r = spotify.get('https://api.spotify.com/v1/me')
    >>> print(r.content)
