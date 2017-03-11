WSO2 OAuth 2 Tutorial
==========================

Setup subscriptions following the instructions on your WSO2 gateway.  When you
have obtained a ``client_id`` and a ``client_secret`` you can try out the
command line interactive example below.


.. code-block:: pycon

    >>> from requests.auth import HTTPBasicAuth
    >>> from oauthlib.oauth2 import BackendApplicationClient
    >>> from requests_oauthlib import OAuth2Session

    >>> #grab client_id and client_secret:
    >>> client_id = u'<clientid>'
    >>> client_secret = u'<secret>'
    >>> token_url = 'https://wso2gateway.myorg.org/token'

    >>> #generate HTTPBasicAuth Header
    >>> basic_auth = HTTPBasicAuth(client_id, client_secret)
    >>> client = BackendApplicationClient(client_id=client_id)
    
    >>> #start oauth session
    >>> oauth = OAuth2Session(client=client)
    >>> token = oauth.fetch_token(token_url=token_url,
                              auth=basic_auth)

    >>> r = oauth.get(u'https://wso2gateway.myorg.org/api/v1/api',
    >>>          headers={'Accept':'application/json'})
    >>> print(r.json())
