OAuth 1 Workflow
================

You will be forced to go through a few steps when you are using OAuth. Below is an
example of the most common OAuth workflow using HMAC-SHA1 signed requests where
the signature is supplied in the Authorization header.

The example assumes an interactive prompt which is good for demonstration but in
practice you will likely be using a web application (which makes authorizing much
less awkward since you can simply redirect).

The guide will show two ways of carrying out the OAuth1 workflow. One using the
authentication helper OAuth1 and the alternative using OAuth1Session. The latter
is usually more convenient and requires less code.

Workflow example showing use of both OAuth1 and OAuth1Session
-------------------------------------------------------------

0. Manual client signup with the OAuth provider (i.e. Google, Twitter) to get
   a set of client credentials. Usually a client key and secret. Client might sometimes
   be referred to as consumer. For example:

.. code-block:: pycon

    >>> # Using OAuth1Session
    >>> from requests_oauthlib import OAuth1Session

    >>> # Using OAuth1 auth helper
    >>> import requests
    >>> from requests_oauthlib import OAuth1

    >>> client_key = '...'
    >>> client_secret = '...'

1. Obtain a request token which will identify you (the client) in the next step.
   At this stage you will only need your client key and secret.

.. code-block:: pycon

    >>> request_token_url = 'https://api.twitter.com/oauth/request_token'

    >>> # Using OAuth1Session
    >>> oauth = OAuth1Session(client_key, client_secret=client_secret)
    >>> fetch_response = oauth.fetch_request_token(request_token_url)
    {
        "oauth_token": "Z6eEdO8MOmk394WozF5oKyuAv855l4Mlqo7hhlSLik",
        "oauth_token_secret": "Kd75W4OQfb2oJTV0vzGzeXftVAwgMnEK9MumzYcM"
    }
    >>> resource_owner_key = fetch_response.get('oauth_token')
    >>> resource_owner_secret = fetch_response.get('oauth_token_secret')

    >>> # Using OAuth1 auth helper
    >>> oauth = OAuth1(client_key, client_secret=client_secret)
    >>> r = requests.post(url=request_token_url, auth=oauth)
    >>> r.content
    "oauth_token=Z6eEdO8MOmk394WozF5oKyuAv855l4Mlqo7hhlSLik&oauth_token_secret=Kd75W4OQfb2oJTV0vzGzeXftVAwgMnEK9MumzYcM"
    >>> from urlparse import parse_qs
    >>> credentials = parse_qs(r.content)
    >>> resource_owner_key = credentials.get('oauth_token')[0]
    >>> resource_owner_secret = credentials.get('oauth_token_secret')[0]

2. Obtain authorization from the user (resource owner) to access their protected
   resources (images, tweets, etc.). This is commonly done by redirecting the
   user to a specific url to which you add the request token as a query parameter.
   Note that not all services will give you a verifier even if they should. Also
   the oauth_token given here will be the same as the one in the previous step.

.. code-block:: pycon

    >>> base_authorization_url = 'https://api.twitter.com/oauth/authorize'

    >>> # Using OAuth1Session
    >>> authorization_url = oauth.authorization_url(base_authorization_url)
    >>> print 'Please go here and authorize,', authorization_url
    >>> redirect_response = raw_input('Paste the full redirect URL here: ')
    >>> oauth_response = oauth.parse_authorization_response(redirect_response)
    {
        "oauth_token": "Z6eEdO8MOmk394WozF5oKyuAv855l4Mlqo7hhlSLik",
        "oauth_verifier": "sdflk3450FASDLJasd2349dfs"
    }
    >>> verifier = oauth_response.get('oauth_verifier')

    >>> # Using OAuth1 auth helper
    >>> authorize_url = base_authorization_url + '?oauth_token='
    >>> authorize_url = authorize_url + resource_owner_key
    >>> print 'Please go here and authorize,', authorize_url
    >>> verifier = raw_input('Please input the verifier')

3. Obtain an access token from the OAuth provider. Save this token as it can be
   re-used later. In this step we will re-use most of the credentials obtained
   uptil this point.

.. code-block:: pycon

    >>> access_token_url = 'https://api.twitter.com/oauth/access_token'

    >>> # Using OAuth1Session
    >>> oauth = OAuth1Session(client_key,
                              client_secret=client_secret,
                              resource_owner_key=resource_owner_key,
                              resource_owner_secret=resource_owner_secret,
                              verifier=verifier)
    >>> oauth_tokens = oauth.fetch_access_token(access_token_url)
    {
        "oauth_token": "6253282-eWudHldSbIaelX7swmsiHImEL4KinwaGloHANdrY",
        "oauth_token_secret": "2EEfA6BG3ly3sR3RjE0IBSnlQu4ZrUzPiYKmrkVU"
    }
    >>> resource_owner_key = oauth_tokens.get('oauth_token')
    >>> resource_owner_secret = oauth_tokens.get('oauth_token_secret')

    >>> # Using OAuth1 auth helper
    >>> oauth = OAuth1(client_key,
                       client_secret=client_secret,
                       resource_owner_key=resource_owner_key,
                       resource_owner_secret=resource_owner_secret,
                       verifier=verifier)
    >>> r = requests.post(url=access_token_url, auth=oauth)
    >>> r.content
    "oauth_token=6253282-eWudHldSbIaelX7swmsiHImEL4KinwaGloHANdrY&oauth_token_secret=2EEfA6BG3ly3sR3RjE0IBSnlQu4ZrUzPiYKmrkVU"
    >>> credentials = parse_qs(r.content)
    >>> resource_owner_key = credentials.get('oauth_token')[0]
    >>> resource_owner_secret = credentials.get('oauth_token_secret')[0]

4. Access protected resources. OAuth1 access tokens typically do not expire
   and may be re-used until revoked by the user or yourself.

.. code-block:: pycon

    >>> protected_url = 'https://api.twitter.com/1/account/settings.json'

    >>> # Using OAuth1Session
    >>> oauth = OAuth1Session(client_key,
                              client_secret=client_secret,
                              resource_owner_key=resource_owner_key,
                              resource_owner_secret=resource_owner_secret)
    >>> r = oauth.get(protected_url)

    >>> # Using OAuth1 auth helper
    >>> oauth = OAuth1(client_key,
                       client_secret=client_secret,
                       resource_owner_key=resource_owner_key,
                       resource_owner_secret=resource_owner_secret)
    >>> r = requests.get(url=protected_url, auth=oauth)


Signature placement - header, query or body?
--------------------------------------------

OAuth takes many forms, so let's take a look at a few different forms:

.. code-block:: python

    import requests
    from requests_oauthlib import OAuth1

    url = u'https://api.twitter.com/1/account/settings.json'

    client_key = u'...'
    client_secret = u'...'
    resource_owner_key = u'...'
    resource_owner_secret = u'...'


Header signing (recommended):

.. code-block:: python

    headeroauth = OAuth1(client_key, client_secret,
                         resource_owner_key, resource_owner_secret,
                         signature_type='auth_header')
    r = requests.get(url, auth=headeroauth)



Query signing:

.. code-block:: python

    queryoauth = OAuth1(client_key, client_secret,
                        resource_owner_key, resource_owner_secret,
                        signature_type='query')
    r = requests.get(url, auth=queryoauth)


Body signing:

.. code-block:: python

    bodyoauth = OAuth1(client_key, client_secret,
                       resource_owner_key, resource_owner_secret,
                       signature_type='body')

    r = requests.post(url, auth=bodyoauth)


Signature types - HMAC (most common), RSA, Plaintext
----------------------------------------------------

OAuth1 defaults to using HMAC and examples can be found in the previous
sections.

Plaintext work on the same credentials as HMAC and the only change you will
need to make when using it is to add signature_type='PLAINTEXT'
to the OAuth1 constructor:

.. code-block:: python

    headeroauth = OAuth1(client_key, client_secret,
                         resource_owner_key, resource_owner_secret,
                         signature_method='PLAINTEXT')

RSA is different in that it does not use client_secret nor
resource_owner_secret. Instead it uses public and private keys. The public key
is provided to the OAuth provider during client registration. The private key
is used to sign requests. The previous section can be summarized as:

.. code-block:: python

    key = open("your_rsa_key.pem").read()

    queryoauth = OAuth1(client_key, signature_method=SIGNATURE_RSA,
                        rsa_key=key, signature_type='query')
    headeroauth = OAuth1(client_key, signature_method=SIGNATURE_RSA,
                        rsa_key=key, signature_type='auth_header')
    bodyoauth = OAuth1(client_key, signature_method=SIGNATURE_RSA,
                        rsa_key=key, signature_type='body')
