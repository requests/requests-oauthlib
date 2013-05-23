Google OAuth 2 Tutorial
==========================

Setup a new web application client in the `Google API console`_
When you have obtained a ``client_id``, ``client_secret`` and registered
a callback URL then you can try out the command line interactive example below.

.. _`Google API console`: https://code.google.com/apis/console/?pli=1

.. code-block:: pycon

    >>> # Credentials you get from registering a new application
    >>> client_id = '<the id you get from google>.apps.googleusercontent.com'
    >>> client_secret = '<the secret you get from google>'
    >>> redirect_uri = 'https://your.registered/callback'

    >>> # OAuth endpoints given in the Google API documentation
    >>> authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
    >>> token_url = "https://accounts.google.com/o/oauth2/token"
    >>> scope = [
    ...     "https://www.googleapis.com/auth/userinfo.email",
    ...     "https://www.googleapis.com/auth/userinfo.profile"
    ... ]

    >>> from requests_oauthlib import OAuth2Session
    >>> google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

    >>> # Redirect user to Google for authorization
    >>> authorization_url, state = google.authorization_url(authorization_base_url,
    ...     # offline for refresh token
    ...     # force to always make user click authorize
    ...     access_type="offline", approval_prompt="force")
    >>> print 'Please go here and authorize,', authorization_url

    >>> # Get the authorization verifier code from the callback url
    >>> redirect_response = raw_input('Paste the full redirect URL here:')

    >>> # Fetch the access token
    >>> google.fetch_token(token_url, client_secret=client_secret,
    ...         authorization_response=redirect_response)

    >>> # Fetch a protected resource, i.e. user profile
    >>> r = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    >>> print r.content
