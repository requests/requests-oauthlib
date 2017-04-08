.. _fitbit:

Fitbit OAuth 2 (Mobile Application Flow) Tutorial
=================================================

This makes use of the Implicit Grant Flow to obtain an access token for the `Fitbit API`_. Register a new client application there with a callback URL, and have your client ID handy. Based on an `another example`_ of the Mobile Application Flow. 

.. _`Fitbit API`: https://dev.fitbit.com/
.. _`another example`: https://github.com/requests/requests-oauthlib/issues/104

.. code-block:: pycon
    
    >>> import requests
    >>> from requests_oauthlib import OAuth2Session
    >>> from oauthlib.oauth2 import MobileApplicationClient

    # Set up your client ID and scope: the scope must match that which you requested when you set up your application.
    >>> client_id = "<your client ID here>"
    >>> scope = ["activity", "heartrate", "location", "nutrition", "profile", "settings", "sleep", "social", "weight"]

    # Initialize client
    >>> client = MobileApplicationClient(client_id)
    >>> fitbit = OAuth2Session(client_id, client=client, scope=scope)
    >>> authorization_url = "https://www.fitbit.com/oauth2/authorize"

    # Grab the URL for Fitbit's authorization page.
    >>> auth_url, state = fitbit.authorization_url(authorization_url)
    >>> print("Visit this page in your browser: {}".format(auth_url))

    # After authenticating, Fitbit will redirect you to the URL you specified in your application settings. It contains the access token.
    >>> callback_url = input("Paste URL you get back here: ")

    # Now we extract the token from the URL to make use of it.
    >>> fitbit.token_from_fragment(callback_url)

    # We can also store the token for use later.
    >>> token = fitbit['token']     

    # At this point, assuming nothing blew up, we can make calls to the API as normal, for example:
    >>> r = fitbit.get('https://api.fitbit.com/1/user/-/sleep/goal.json')
