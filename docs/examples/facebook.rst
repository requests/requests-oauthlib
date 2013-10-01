Facebook OAuth 2 Tutorial
=========================

Setup a new web application client in the `Facebook APP console`_
When you have obtained a ``client_id``, ``client_secret`` and registered
a callback URL then you can try out the command line interactive example below.

.. _`Facebook APP console`: https://developers.facebook.com/apps

.. code-block:: pycon

    >>> # Credentials you get from registering a new application
    >>> client_id = '<the id you get from facebook>'
    >>> client_secret = '<the secret you get from facebook>'

    >>> # OAuth endpoints given in the Facebook API documentation
    >>> authorization_base_url = 'https://www.facebook.com/dialog/oauth'
    >>> token_url = 'https://graph.facebook.com/oauth/access_token'
    >>> redirect_uri = 'https://localhost/'     # Should match Site URL

    >>> from requests_oauthlib import OAuth2Session
    >>> from requests_oauthlib.compliance_fixes import facebook_compliance_fix
    >>> facebook = OAuth2Session(client_id, redirect_uri=redirect_uri)
    >>> facebook = facebook_compliance_fix(facebook)

    >>> # Redirect user to Facebook for authorization
    >>> authorization_url, state = facebook.authorization_url(authorization_base_url)
    >>> print 'Please go here and authorize,', authorization_url

    >>> # Get the authorization verifier code from the callback url
    >>> redirect_response = raw_input('Paste the full redirect URL here:')

    >>> # Fetch the access token
    >>> facebook.fetch_token(token_url, client_secret=client_secret,
    ..>                      authorization_response=redirect_response)

    >>> # Fetch a protected resource, i.e. user profile
    >>> r = facebook.get('https://graph.facebook.com/me?')
    >>> print r.content
