MediaWiki OAuth 1 Tutorial
==========================

Start with setting up a new consumer by following the instructions on
`MediaWiki`_. When you have obtained a ``key`` and a ``secret`` you can
try out the command line interactive example below.

You'll also have to set a callback url while registering.

See also this library implementing all the flow below, plus the `/identify` custom call: `mwoauth`_.

.. _`MediaWiki`: https://www.mediawiki.org/wiki/Extension:OAuth#Using_OAuth
.. _`mwoauth`: https://github.com/halfak/MediaWiki-OAuth

Using OAuth1Session
-------------------

.. code-block:: python

    from requests_oauthlib import OAuth1Session

    # Get the anonymous oauth_token and secret
    request_token_url = 'https://www.mediawiki.org/w/index.php?title=Special%3aOAuth%2finitiate'
    # Note the custom callback_uri arg!
    oauth = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri='oob')
    fetch_response = oauth.fetch_request_token(request_token_url)
    # fetch_response: {u'oauth_token_secret': u'3768a660fcdc5ba958268decc11bf590', u'oauth_token': u'5d684692fe129665c9f967f54bbc525d', u'oauth_callback_confirmed': u'true'}
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    # Redirect the user to /authorize and get the callback
    base_authorization_url = 'https://www.mediawiki.org/wiki/Special:OAuth/authorize'
    # Note the extra oauth_consumer_key argument!
    authorization_url = oauth.authorization_url(base_authorization_url, oauth_consumer_key=CLIENT_KEY)
    print 'Please go here and authorize,', authorization_url
    # OUT: Please go here and authorize, https://www.mediawiki.org/wiki/Special:OAuth/authorize?oauth_consumer_key=85c9f176fcb96952f1b3b967cbb4ef9e&oauth_token=5d684692fe129665c9f967f54bbc525d
    redirect_response = raw_input('Paste the full redirect URL here: ')
    # OUT: Paste the full redirect URL here: https://snuggle.wmflabs.org/oauth/callback?oauth_verifier=7f98e940b58745e14602e0522c7e5e90&oauth_token=5d684692fe129665c9f967f54bbc525d
    oauth_response = oauth.parse_authorization_response(redirect_response)
    # oauth_response: {u'oauth_token': u'5d684692fe129665c9f967f54bbc525d', u'oauth_verifier': u'7f98e940b58745e14602e0522c7e5e90'}
    verifier = oauth_response.get('oauth_verifier')

    # Get the final oauth_token and secret
    access_token_url = 'https://www.mediawiki.org/w/index.php?title=Special%3aOAuth%2ftoken'
    oauth = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret, verifier=verifier)
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    # oauth_tokens: {u'oauth_token_secret': u'10e284c0ce48c2c2c6ce4f58fca358d6ff495a55', u'oauth_token': u'2f227cce369edad1ff3880bb4dab84f2', u'oauth_callback_confirmed': u'true'}
    resource_owner_key = oauth_tokens.get('oauth_token')
    resource_owner_secret = oauth_tokens.get('oauth_token_secret')

    # Make authenticated calls to the API
    data = {'action': 'query', 'meta': 'userinfo', 'format': 'json'}
    from urllib import urlencode
    url = 'https://www.mediawiki.org/w/api.php?' + urlencode(data)
    oauth = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret)
    r = oauth.get(url)
    r.json()
    # OUT: {u'query': {u'userinfo': {u'id': 32663, u'name': u'FiloSottile'}}}


Using OAuth1 auth helper (stateless)
------------------------------------

.. code-block:: python

    import requests
    from requests_oauthlib import OAuth1

    # Get the anonymous oauth_token and secret
    request_token_url = 'https://www.mediawiki.org/w/index.php?title=Special%3aOAuth%2finitiate'
    oauth = OAuth1(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri='oob')
    r = requests.post(url=request_token_url, auth=oauth)
    r.content
    # OUT: 'oauth_token=d44ce3a59d2d8cbcc0ebbae4d0157f4a&oauth_token_secret=a10676b7e6c4ae44db1411d1dece9267&oauth_callback_confirmed=true'
    from urlparse import parse_qs
    credentials = parse_qs(r.content)
    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Redirect the user to /authorize and get the callback
    base_authorization_url = 'https://www.mediawiki.org/wiki/Special:OAuth/authorize'
    authorize_url = base_authorization_url + '?oauth_token=' + resource_owner_key + '&oauth_consumer_key=' + CLIENT_KEY
    print 'Please go here and authorize,', authorize_url
    # OUT: Please go here and authorize, https://www.mediawiki.org/wiki/Special:OAuth/authorize?oauth_token=d44ce3a59d2d8cbcc0ebbae4d0157f4a&oauth_consumer_key=85c9f176fcb96952f1b3b967cbb4ef9e
    callback_qs = raw_input('Please input the callback query string: ')
    # OUT: Please input the callback query string: oauth_verifier=5eb313f9b4006e922c3e4a7d2493df98&oauth_token=d44ce3a59d2d8cbcc0ebbae4d0157f4a
    callback_data = parse_qs(callback_qs)
    verifier = callback_data.get('oauth_verifier')[0]
    assert callback_data.get('oauth_token')[0] == resource_owner_key

    # Get the final oauth_token and secret
    access_token_url = 'https://www.mediawiki.org/w/index.php?title=Special%3aOAuth%2ftoken'
    oauth = OAuth1(CLIENT_KEY, client_secret=CLIENT_SECRET, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret, verifier=verifier)
    r = requests.post(url=access_token_url, auth=oauth)
    r.content
    # OUT: 'oauth_token=2f227cce369edad1ff3880bb4dab84f2&oauth_token_secret=10e284c0ce48c2c2c6ce4f58fca358d6ff495a55&oauth_callback_confirmed=true'
    credentials = parse_qs(r.content)
    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Make authenticated calls to the API
    data = {'action': 'query', 'meta': 'userinfo', 'format': 'json'}
    from urllib import urlencode
    url = 'https://www.mediawiki.org/w/api.php?' + urlencode(data)
    oauth = OAuth1(CLIENT_KEY, client_secret=CLIENT_SECRET, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret)
    r = requests.get(url=url, auth=oauth)
    r.json()
    # OUT: {u'query': {u'userinfo': {u'id': 32663, u'name': u'FiloSottile'}}}
