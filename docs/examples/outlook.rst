Outlook Calendar OAuth 2 Tutorial
=================================

Create a new web application client in the `Microsoft Application Registration Portal`_
When you have obtained a ``client_id``, ``client_secret`` and registered
a callback URL then you can try out the command line interactive example below.

.. _`Outlook App console`: https://apps.dev.microsoft.com

.. code-block:: pycon

    >>> # This information is obtained upon registration of a new Outlook Application
    >>> client_id = '<the id you get from outlook>'
    >>> client_secret = '<the secret you get from outlook>'

    >>> # OAuth endpoints given in Outlook API documentation
    >>> authorization_base_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    >>> token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    >>> scope = ['https://outlook.office.com/calendars.readwrite']
    >>> redirect_uri = 'https://localhost/'     # Should match Site URL

    >>> from requests_oauthlib import OAuth2Session
    >>> outlook = OAuth2Session(client_id,scope=scope,redirect_uri=redirect_uri)

    >>> # Redirect  the user owner to the OAuth provider (i.e. Outlook) using an URL with a few key OAuth parameters.
    >>> authorization_url, state = outlook.authorization_url(authorization_base_url)
    >>> print 'Please go here and authorize,', authorization_url

    >>> # Get the authorization verifier code from the callback url
    >>> redirect_response = raw_input('Paste the full redirect URL here:')

    >>> # Fetch the access token
    >>> token = outlook.fetch_token(token_url,client_secret=client_secret,authorization_response=redirect_response)

    >>> # Fetch a protected resource, i.e. calendar information
    >>> o = outlook.get('https://outlook.office.com/api/v1.0/me/calendars')
    >>> print o.content
