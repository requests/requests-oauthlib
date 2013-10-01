Bitbucket OAuth 1 Tutorial
==========================

Start with setting up a new consumer by following the instructions on
`Bitbucket`_. When you have obtained a ``key`` and a ``secret`` you can
try out the command line interactive example below.

.. _`Bitbucket`: https://confluence.atlassian.com/display/BITBUCKET/OAuth+on+Bitbucket

.. code-block:: pycon

    # Credentials you get from adding a new consumer in bitbucket -> manage account
    # -> integrated applications.
    >>> key = '<the key you get from bitbucket>'
    >>> secret = '<the secret you get from bitbucket>'

    >>> # OAuth endpoints given in the Bitbucket API documentation
    >>> request_token_url = 'https://bitbucket.org/!api/1.0/oauth/request_token'
    >>> authorization_base_url = 'https://bitbucket.org/!api/1.0/oauth/authenticate'
    >>> access_token_url = 'https://bitbucket.org/!api/1.0/oauth/access_token'

    >>> # 2. Fetch a request token
    >>> from requests_oauthlib import OAuth1Session
    >>> bitbucket = OAuth1Session(key, client_secret=secret,
    >>>         callback_uri='http://127.0.0.1/cb')
    >>> bitbucket.fetch_request_token(request_token_url)

    >>> # 3. Redirect user to Bitbucket for authorization
    >>> authorization_url = bitbucket.authorization_url(authorization_base_url)
    >>> print 'Please go here and authorize,', authorization_url

    >>> # 4. Get the authorization verifier code from the callback url
    >>> redirect_response = raw_input('Paste the full redirect URL here:')
    >>> bitbucket.parse_authorization_response(redirect_response)

    >>> # 5. Fetch the access token
    >>> bitbucket.fetch_access_token(access_token_url)

    >>> # 6. Fetch a protected resource, i.e. user profile
    >>> r = bitbucket.get('https://bitbucket.org/api/1.0/user')
    >>> print r.content
