Requests-OAuthlib
=================

This project provides first-class OAuth library support for `Requests <http://python-requests.org>`_.

Usage
-----

OAuth takes many forms, so let's take a look at a few different forms::

    import requests
    from requests_authlib import OAuth1

    url = u'https://api.twitter.com/1/account/settings.json'

    client_key = u'...'
    client_secret = u'...'
    resource_owner_key = u'...'
    resource_owner_secret = u'...'


Query signing::

    queryoauth = OAuth1(client_key, client_secret,
                        resource_owner_key, resource_owner_secret,
                        signature_type='query')
    r = requests.get(url, auth=queryoauth)

Header signing::

    headeroauth = OAuth1(client_key, client_secret,
                         resource_owner_key, resource_owner_secret,
                         signature_type='auth_header')
    r = requests.get(url, auth=headeroauth)

Body signing::

    bodyoauth = OAuth1(client_key, client_secret,
                       resource_owner_key, resource_owner_secret,
                       signature_type='body')

    r = requests.post(url, auth=bodyoauth)


Installation
-------------


To install requests, you can use pip::

    $ pip install requests

