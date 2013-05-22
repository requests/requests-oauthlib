OAuth 2 Workflow
================

0. Obtaining credentials from your OAuth provider manually. You will need
   at minimum a ``client_id`` but likely also a ``client_secret``. During
   this process you might also be required to register a default redirect
   URI to be used by your application:

.. code-block:: pycon

    >>> client_id = 'your_client_id'
    >>> client_secret = 'your_client_secret'
    >>> redirect_uri = 'https://your.callback/uri'

1. User authorization through redirection. First we will create an
   authorization url from the base URL given by the provider and
   the credentials previously obtained. In addition most providers will
   request that you ask for access to a certain scope, in this example
   we will ask Google for access to the email address of the user and the
   users profile.

.. code-block:: pycon

    # Note that these are Google specific scopes
    >>> scope = ['https://www.googleapis.com/auth/userinfo.email',
                 'https://www.googleapis.com/auth/userinfo.profile']
    >>> oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,
                              scope=scope)
    >>> authorization_url, state = oauth.authorization_url(
            'https://accounts.google.com/o/oauth2/auth',
            # access_type and approval_prompt are Google specific extra
            # parameters. 
            access_type="offline", approval_prompt="force")

    >>> print 'Please go to %s and authorize access.' % authorization_url
    >>> authorization_response = raw_input('Enter the full callback URL') 

2. Fetch an access token from the provider using the authorization code
   obtained during user authorization:

.. code-block:: pycon

    >>> token = oauth.fetch_token(
            'https://accounts.google.com/o/oauth2/token',
            authorization_response=authorization_response,
            # Google specific extra parameter used for client
            # authentication
            client_secret=secret)

3. Access protected resources using the access token you just obtained.
   For example, get the users profile info.

.. code-block:: pycon

    >>> r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
    >>> # Enjoy =)


Available workflows
-------------------

TODO: outline implicit, password and client credentials flows.

Refreshing tokens
-----------------

TODO: demonstrate how to refresh tokens.
