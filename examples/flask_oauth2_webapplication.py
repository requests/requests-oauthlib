import flask
import os

from requests_oauthlib import OAuth2Client, TokenUpdated
from oauthlib.oauth2 import TokenExpiredError

app = flask.Flask(__name__)

# This information is obtained upon registration of a new client in
# the Google API console
client_id = "<your client key>"
redirect_uri = "http://127.0.0.1:5000/callback"

# The secret is used for authentication
secret = "<your client secret>"

# Google specific endpoints
authorization_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
refresh_url = token_url

# Random protected resource
protected_url = "https://www.googleapis.com/oauth2/v1/userinfo"
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


@app.route("/")
def pre_authorization():
    # Let the user authorize access to scope by redirecting them to
    # the provider which then redirects them back to us (/callback)

    client = OAuth2Client(client_id, redirect_uri=redirect_uri, scope=scope)
    full_authorization_url, state = client.authorization_url(authorization_url,
            # These are Google specific extra parameters
            access_type="offline", approval_prompt="force")
    # Need to save state for next step, not that you really should not use
    # sessions for this as it's insecure but it works for demonstrative
    # purposes. You will rather want to bind the state to this session in a db.
    flask.session['state'] = state
    return flask.redirect(full_authorization_url)


@app.route("/callback", methods=["GET"])
def post_authorization():
    # User is back from the provider, hopefully carrying an authorization code
    # and not an error...

    # Fetch previously saved state
    state = flask.session['state']
    # We will let OAuth2Client parse the code out from the URL for us
    url = flask.request.url
    client = OAuth2Client(client_id, redirect_uri=redirect_uri, scope=scope,
            state=state)
    # Fetch the token from the token endpoint, will cause a POST request.
    token = client.fetch_token(token_url, authorization_response=url,
                # Google specific extra parameter used for client authentication
                client_secret=secret)
    # Save token for later use, once again this should be in a db, not session
    flask.session['token'] = token

    # By this point you are essentially done with the OAuth 2 auth grant flow

    # Let's fetch something protected
    r = client.get(protected_url)
    return r.content


@app.route("/later", methods=["GET"])
def later():
    # Fetch previously saved token, no need to do auth dance while its valid
    token = flask.session['token']
    client = OAuth2Client(client_id, token=token)

    # Let's fetch something protected
    r = client.get(protected_url)
    return r.content


@app.route("/refresh", methods=["GET"])
def refresh():
    # Access tokens expire quickly, usually an hour, let's try refresh.
    # Refresh will happen automatically if using auto_refresh. If not a
    # TokenExpiredError will be raised.
    # Token will be updated is using token_updater.

    def token_updater(token):
        flask.session['token'] = token

    # Google specific extra refresh args
    extra = {
        'client_id': client_id,
        'client_secret': secret
    }

    # With auto refresh and token updating
    token = flask.session['token']
    token['expires_in'] = '-300'    # Force expiration
    client = OAuth2Client(client_id, token=token, auto_refresh_url=refresh_url,
            auto_refresh_kwargs=extra, token_updater=token_updater)
    r = client.get(protected_url)

    # With auto refresh and catching token updates
    token = flask.session['token']
    token['expires_in'] = '-300'    # Force expiration
    try:
        client = OAuth2Client(client_id, token=token,
                auto_refresh_kwargs=extra, auto_refresh_url=refresh_url)
        r = client.get(protected_url)
    except TokenUpdated as e:
        token_updater(e.token)

    # Without auto refresh and catching token expired
    token = flask.session['token']
    token['expires_in'] = '-300'    # Force expiration
    try:
        client = OAuth2Client(client_id, token=token)
        r = client.get(protected_url)
    except TokenExpiredError as e:
        token = client.refresh_token(refresh_url, **extra)
        token_updater(token)

    # Let's fetch something protected
    token = flask.session['token']
    r = client.get(protected_url)
    return r.content

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
