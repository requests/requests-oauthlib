GitHub OAuth 2 Tutorial
==========================

Setup credentials following the instructions on `GitHub`_.  When you
have obtained a ``client_id`` and a ``client_secret`` you can try out the
command line interactive example below.

.. _`GitHub`: https://github.com/settings/applications/new

.. code-block:: pycon

    >>> # Credentials you get from registering a new application
    >>> client_id = '<the id you get from github>'
    >>> client_secret = '<the secret you get from github>'

    >>> # OAuth endpoints given in the GitHub API documentation
    >>> authorization_base_url = 'https://github.com/login/oauth/authorize'
    >>> token_url = 'https://github.com/login/oauth/access_token'

    >>> from requests_oauthlib import OAuth2Session
    >>> github = OAuth2Session(client_id)

    >>> # Redirect user to GitHub for authorization
    >>> authorization_url, state = github.authorization_url(authorization_base_url)
    >>> print 'Please go here and authorize,', authorization_url

    >>> # Get the authorization verifier code from the callback url
    >>> redirect_response = raw_input('Paste the full redirect URL here:')

    >>> # Fetch the access token
    >>> github.fetch_token(token_url, client_secret=client_secret,
    >>>         authorization_response=redirect_response)

    >>> # Fetch a protected resource, i.e. user profile
    >>> r = github.get('https://api.github.com/user')
    >>> print r.content
