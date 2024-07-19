GitLab OAuth 2 Tutorial
==========================

Add a new application on `GitLab`_ (redirect URI can be `https://example.com`
and check the box `read_user`).  When you have obtained a ``client_id`` and a
``client_secret`` you can try out the command line interactive example below.

.. _`GitLab`:
https://gitlab.com/-/user_settings/applications

.. code-block:: pycon


    >>> # Credentials you get from registering a new application
    >>> client_id = '<the id you get from github>'
    >>> client_secret = '<the secret you get from github>'
    >>> redirect_uri = '<the URI you gave>'
    >>> scope = '<the scope you checked>'

    >>> # OAuth endpoints given in the GitLab API documentation
    >>> authorization_base_url = 'https://gitlab.com/oauth/authorize'
    >>> token_url = 'https://gitlab.com/oauth/token'

    >>> from requests_oauthlib import OAuth2Session
    >>> gitlab = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

    >>> # Redirect user to GitLab for authorization
    >>> authorization_url, state = gitlab.authorization_url(authorization_base_url)
    >>> print('Please go here and authorize,', authorization_url)

    >>> # Get the authorization verifier code from the callback url
    >>> redirect_response = input('Paste the full redirect URL here:')

    >>> # Fetch the access token
    >>> gitlab.fetch_token(token_url, client_secret=client_secret,
    >>>         authorization_response=redirect_response)

    >>> # Fetch a protected resource, i.e. user profile
    >>> r = gitlab.get('https://gitlab.com/api/v4/users')
    >>> print(r.content)

    >>> # Refresh the token
    >>> refresh_url = token_url # True for GitLab but not all providers.
    >>> gitlab.refresh_token(refresh_url,
    >>>         client_id=client_id, client_secret=client_secret)

    >>> # Revoke the token
    >>> revoke_url = 'https://gitlab.com/oauth/revoke'
    >>> gitlab.revoke_token(revoke_url,
    >>>         client_id=client_id, client_secret=client_secret)
