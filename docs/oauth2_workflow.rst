OAuth 2 Workflow
================

.. contents::
    :depth: 3
    :local:


Introduction
------------

The following sections provide some example code that demonstrates some of the
possible OAuth2 flows you can use with requests-oauthlib. We provide four
examples: one for each of the grant types defined by the OAuth2 RFC. These
grant types (or workflows) are the Authorization Code Grant (or Web Application
Flow), the Implicit Grant (or Mobile Application Flow), the Resource Owner
Password Credentials Grant (or, more succinctly, the Legacy Application Flow),
and the Client Credentials Grant (or Backend Application Flow).


Available Workflows
~~~~~~~~~~~~~~~~~~~

There are four core work flows:

1. :ref:`Authorization Code Grant <web-application-flow>` (Web Application
   Flow).
2. :ref:`Implicit Grant <mobile-application-flow>` (Mobile Application flow).
3. :ref:`Resource Owner Password Credentials Grant <legacy-application-flow>`
   (Legacy Application flow).
4. :ref:`Client Credentials Grant <backend-application-flow>` (Backend
   Application flow).


.. _web-application-flow:

Web Application Flow
--------------------

The steps below outline how to use the default Authorization Grant Type flow to
obtain an access token and fetch a protected resource. In this example
the provider is Google and the protected resource is the user's profile.

0. Obtain credentials from your OAuth provider manually. At minimum you will
   need a ``client_id`` but likely also a ``client_secret``. During this
   process you might also be required to register a default redirect URI to be
   used by your application. Save these things in your Python script:

.. code-block:: pycon

    >>> client_id = r'your_client_id'
    >>> client_secret = r'your_client_secret'
    >>> redirect_uri = 'https://your.callback/uri'

1. User authorization through redirection. First we will create an
   authorization url from the base URL given by the provider and
   the credentials previously obtained. In addition most providers will
   request that you ask for access to a certain scope. In this example
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
            # access_type and prompt are Google specific extra
            # parameters.
            access_type="offline", prompt="select_account")

    >>> print(f'Please go to {authorization_url} and authorize access.')
    >>> authorization_response = input('Enter the full callback URL')

2. Fetch an access token from the provider using the authorization code
   obtained during user authorization.

.. code-block:: pycon

    >>> token = oauth.fetch_token(
            'https://accounts.google.com/o/oauth2/token',
            authorization_response=authorization_response,
            # Google specific extra parameter used for client
            # authentication
            client_secret=client_secret)

3. Access protected resources using the access token you just obtained.
   For example, get the users profile info.

.. code-block:: pycon

    >>> r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
    >>> # Enjoy =)


.. _mobile-application-flow:

Mobile Application Flow
-----------------------

The steps below outline how to use the Implicit Code Grant Type flow to obtain an access token.

0. You will need the following settings.

.. code-block:: pycon

    >>> client_id = 'your_client_id'
    >>> scopes = ['scope_1', 'scope_2']
    >>> auth_url = 'https://your.oauth2/auth'

1. Get the authorization_url

.. code-block:: pycon

    >>> from oauthlib.oauth2 import MobileApplicationClient
    >>> from requests_oauthlib import OAuth2Session
    >>> oauth = OAuth2Session(client=MobileApplicationClient(client_id=client_id), scope=scopes)
    >>> authorization_url, state = oauth.authorization_url(auth_url)

2. Fetch an access token from the provider.

.. code-block:: pycon

    >>> response = oauth.get(authorization_url)
    >>> oauth.token_from_fragment(response.url)


.. _legacy-application-flow:

Legacy Application Flow
-----------------------

The steps below outline how to use the Resource Owner Password Credentials Grant Type flow to obtain an access token.

0. You will need the following settings. ``client_secret`` is optional depending on the provider.

.. code-block:: pycon

    >>> client_id = 'your_client_id'
    >>> client_secret = 'your_client_secret'
    >>> username = 'your_username'
    >>> password = 'your_password'

1. Fetch an access token from the provider.

.. code-block:: pycon

    >>> from oauthlib.oauth2 import LegacyApplicationClient
    >>> from requests_oauthlib import OAuth2Session
    >>> oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
    >>> token = oauth.fetch_token(token_url='https://somesite.com/oauth2/token',
            username=username, password=password, client_id=client_id,
            client_secret=client_secret)

.. _backend-application-flow:

Backend Application Flow
------------------------

The steps below outline how to use the Resource Owner Client Credentials Grant Type flow to obtain an access token.

0. Obtain credentials from your OAuth provider. At minimum you will
   need a ``client_id`` and ``client_secret``.

    .. code-block:: pycon

        >>> client_id = 'your_client_id'
        >>> client_secret = 'your_client_secret'

1. Fetch an access token from the provider.

    .. code-block:: pycon

        >>> from oauthlib.oauth2 import BackendApplicationClient
        >>> from requests_oauthlib import OAuth2Session
        >>> client = BackendApplicationClient(client_id=client_id)
        >>> oauth = OAuth2Session(client=client)
        >>> token = oauth.fetch_token(token_url='https://provider.com/oauth2/token', client_id=client_id,
                client_secret=client_secret)

   If your provider requires that you pass auth credentials in a Basic Auth header, you can do this instead:

    .. code-block:: pycon

        >>> from oauthlib.oauth2 import BackendApplicationClient
        >>> from requests_oauthlib import OAuth2Session
        >>> from requests.auth import HTTPBasicAuth
        >>> auth = HTTPBasicAuth(client_id, client_secret)
        >>> client = BackendApplicationClient(client_id=client_id)
        >>> oauth = OAuth2Session(client=client)
        >>> token = oauth.fetch_token(token_url='https://provider.com/oauth2/token', auth=auth)

Refreshing tokens
-----------------

Certain providers will give you a ``refresh_token`` along with the
``access_token``. These can be used to directly fetch new access tokens without
going through the normal OAuth workflow. ``requests-oauthlib`` provides three
methods of obtaining refresh tokens. All of these are dependent on you
specifying an accurate ``expires_in`` in the token.

``expires_in`` is a credential given with the access and refresh token
indicating in how many seconds from now the access token expires. Commonly,
access tokens expire after an hour and the ``expires_in`` would be ``3600``.
Without this it is impossible for ``requests-oauthlib`` to know when a token
is expired as the status code of a request failing due to token expiration is
not defined.

If you are not interested in token refreshing, always pass in a positive value
for ``expires_in`` or omit it entirely.

(ALL) Define the token, token saver and needed credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: pycon

    >>> token = {
    ...     'access_token': 'eswfld123kjhn1v5423',
    ...     'refresh_token': 'asdfkljh23490sdf',
    ...     'token_type': 'Bearer',
    ...     'expires_in': '-30',     # initially 3600, need to be updated by you
    ...  }
    >>> client_id = r'foo'
    >>> refresh_url = 'https://provider.com/token'
    >>> protected_url = 'https://provider.com/secret'

    >>> # most providers will ask you for extra credentials to be passed along
    >>> # when refreshing tokens, usually for authentication purposes.
    >>> extra = {
    ...     'client_id': client_id,
    ...     'client_secret': r'potato',
    ... }

    >>> # After updating the token you will most likely want to save it.
    >>> def token_saver(token):
    ...     # save token in database / session

(First) Define Try-Catch TokenExpiredError on each request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the most basic version in which an error is raised when refresh
is necessary but refreshing is done manually.

.. code-block:: pycon

    >>> from requests_oauthlib import OAuth2Session
    >>> from oauthlib.oauth2 import TokenExpiredError
    >>> try:
    ...     oauth = OAuth2Session(client_id, token=token)
    ...     r = oauth.get(protected_url)
    >>> except TokenExpiredError as e:
    ...     token = oauth.refresh_token(refresh_url, **extra)
    ...     token_saver(token)
    >>> oauth = OAuth2Session(client_id, token=token)
    >>> r = oauth.get(protected_url)

(Second) Define automatic token refresh automatic but update manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the, arguably awkward, middle between the basic and convenient refresh
methods in which a token is automatically refreshed, but saving the new token
is done manually.

.. code-block:: pycon

    >>> from requests_oauthlib import OAuth2Session, TokenUpdated
    >>> try:
    ...     oauth = OAuth2Session(client_id, token=token,
    ...             auto_refresh_kwargs=extra, auto_refresh_url=refresh_url)
    ...     r = oauth.get(protected_url)
    >>> except TokenUpdated as e:
    ...     token_saver(e.token)

(Third, Recommended) Define automatic token refresh and update
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The third and recommended method will automatically fetch refresh tokens and
save them. It requires no exception catching and results in clean code. Remember
however that you still need to update ``expires_in`` to trigger the refresh.

.. code-block:: pycon

    >>> from requests_oauthlib import OAuth2Session
    >>> oauth = OAuth2Session(client_id, token=token, auto_refresh_url=refresh_url,
    ...     auto_refresh_kwargs=extra, token_updater=token_saver)
    >>> r = oauth.get(protected_url)


Revoking tokens
---------------

Certain providers will provide a ``revoke`` API. It can be used to revoke the
access token or the refresh token.

.. code-block:: pycon

    >>> token = {
    ...     'access_token': 'eswfld123kjhn1v5423',
    ...     'refresh_token': 'asdfkljh23490sdf',
    ...     'token_type': 'Bearer',
    ...     'expires_in': '-30',     # initially 3600, need to be updated by you
    ...  }
    >>> client_id = r'foo'
    >>> revoke_url = 'https://provider.com/revoke'

    >>> # some providers will ask you for extra credentials to be passed along
    >>> # when refreshing tokens, usually for authentication purposes.
    >>> extra = {
    ...     'client_id': client_id,
    ...     'client_secret': r'potato',
    ... }

    >>> from requests_oauthlib import OAuth2Session
    >>> from oauthlib.oauth2 import TokenExpiredError
    >>> oauth = OAuth2Session(client_id, token=token)
    >>> oauth.revoke_token(revoke_url, **extra)

TLS Client Authentication
-------------------------

To use TLS Client Authentication (draft-ietf-oauth-mtls) via a
self-signed or CA-issued certificate, pass the certificate in the
token request and ensure that the client id is sent in the request:

.. code-block:: pycon

   >>> oauth.fetch_token(token_url='https://somesite.com/oauth2/token',
   ...     include_client_id=True, cert=('test-client.pem', 'test-client-key.pem'))

.. _write this section: https://github.com/requests/requests-oauthlib/issues/48
