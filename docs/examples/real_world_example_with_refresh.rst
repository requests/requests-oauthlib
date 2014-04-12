.. _token_refresh:

Refreshing tokens in OAuth 2
============================

OAuth 2 providers may allow you to refresh access tokens using refresh tokens.
Commonly, only clients that authenticate may refresh tokens, e.g. web applications
but not javascript clients. The provider will mention whether they allow token
refresh in their API documentation and if you see a "refresh_token" in your
token response you are good to go.

This example shows how a simple web application (using the `Flask web framework
<http://flask.pocoo.org/>`_) can refresh Google OAuth 2 tokens. It should be
trivial to transfer to any other web framework and provider.

.. code-block:: python

    from pprint import pformat
    from time import time

    from flask import Flask, request, redirect, session, url_for
    from flask.json import jsonify
    import requests
    from requests_oauthlib import OAuth2Session

    app = Flask(__name__)

    # This information is obtained upon registration of a new Google OAuth
    # application at https://code.google.com/apis/console
    client_id = "<your client key>"
    client_secret = "<your client secret>"
    redirect_uri = 'https://your.registered/callback'

    # Uncomment for detailed oauthlib logs
    #import logging
    #import sys
    #log = logging.getLogger('oauthlib')
    #log.addHandler(logging.StreamHandler(sys.stdout))
    #log.setLevel(logging.DEBUG)

    # OAuth endpoints given in the Google API documentation
    authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://accounts.google.com/o/oauth2/token"
    refresh_url = token_url # True for Google but not all providers.
    scope = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    @app.route("/")
    def demo():
        """Step 1: User Authorization.

        Redirect the user/resource owner to the OAuth provider (i.e. Google)
        using an URL with a few key OAuth parameters.
        """
        google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
        authorization_url, state = google.authorization_url(authorization_base_url,
            # offline for refresh token
            # force to always make user click authorize
            access_type="offline", approval_prompt="force")

        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        return redirect(authorization_url)


    # Step 2: User authorization, this happens on the provider.
    @app.route("/callback", methods=["GET"])
    def callback():
        """ Step 3: Retrieving an access token.

        The user has been redirected back from the provider to your registered
        callback URL. With this redirection comes an authorization code included
        in the redirect URL. We will use that to obtain an access token.
        """

        google = OAuth2Session(client_id, redirect_uri=redirect_uri,
                               state=session['oauth_state'])
        token = google.fetch_token(token_url, client_secret=client_secret,
                                   authorization_response=request.url)

        # We use the session as a simple DB for this example.
        session['oauth_token'] = token

        return redirect(url_for('.menu'))


    @app.route("/menu", methods=["GET"])
    def menu():
        """"""
        return """
        <h1>Congratulations, you have obtained an OAuth 2 token!</h1>
        <h2>What would you like to do next?</h2>
        <ul>
            <li><a href="/profile"> Get account profile</a></li>
            <li><a href="/automatic_refresh"> Implicitly refresh the token</a></li>
            <li><a href="/manual_refresh"> Explicitly refresh the token</a></li>
            <li><a href="/validate"> Validate the token</a></li>
        </ul>

        <pre>
        %s
        </pre>
        """ % pformat(session['oauth_token'], indent=4)


    @app.route("/profile", methods=["GET"])
    def profile():
        """Fetching a protected resource using an OAuth 2 token.
        """
        google = OAuth2Session(client_id, token=session['oauth_token'])
        return jsonify(google.get('https://www.googleapis.com/oauth2/v1/userinfo').json())


    @app.route("/automatic_refresh", methods=["GET"])
    def automatic_refresh():
        """Refreshing an OAuth 2 token using a refresh token.
        """
        token = session['oauth_token']

        # We force an expiration by setting expired at in the past.
        # This will trigger an automatic refresh next time we interact with
        # Googles API.
        token['expires_at'] = time() - 10

        extra = {
            'client_id': client_id,
            'client_secret': client_secret,
        }

        def token_updater(token):
            session['oauth_token'] = token

        google = OAuth2Session(client_id,
                               token=token,
                               auto_refresh_kwargs=extra,
                               auto_refresh_url=refresh_url,
                               token_updater=token_updater)

        # Trigger the automatic refresh
        jsonify(google.get('https://www.googleapis.com/oauth2/v1/userinfo').json())
        return jsonify(session['oauth_token'])


    @app.route("/manual_refresh", methods=["GET"])
    def manual_refresh():
        """Refreshing an OAuth 2 token using a refresh token.
        """
        token = session['oauth_token']

        extra = {
            'client_id': client_id,
            'client_secret': client_secret,
        }

        google = OAuth2Session(client_id, token=token)
        session['oauth_token'] = google.refresh_token(refresh_url, **extra)
        return jsonify(session['oauth_token'])

    @app.route("/validate", methods=["GET"])
    def validate():
        """Validate a token with the OAuth provider Google.
        """
        token = session['oauth_token']

        # Defined at https://developers.google.com/accounts/docs/OAuth2LoginV1#validatingtoken
        validate_url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?'
                        'access_token=%s' % token['access_token'])

        # No OAuth2Session is needed, just a plain GET request
        return jsonify(requests.get(validate_url).json())


    if __name__ == "__main__":
        # This allows us to use a plain HTTP callback
        import os
        os.environ['DEBUG'] = "1"

        app.secret_key = os.urandom(24)
        app.run(debug=True)
