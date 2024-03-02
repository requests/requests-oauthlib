
client_id = 'OAUTH_CLIENT_ID'

authorization_base_url = "https://OAUTH_IDP_DOMAIN/authorize"
token_url = "https://OAUTH_IDP_DOMAIN/oauth/token"
scope = ["openid"]

from requests_oauthlib import OAuth2Session
redirect_uri = 'http://localhost:8080/callback'

session = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri, pkce="S256")
authorization_url, state = session.authorization_url(authorization_base_url,access_type="offline")

print("Please go here and authorize:")
print(authorization_url)

redirect_response = input('Paste the full redirect URL here: ')

token = session.fetch_token(token_url, authorization_response=redirect_response, include_client_id=True)
print(token)
