History
-------

v0.4.0 (29 September 2013)
++++++++++++++++++++++++++
- OAuth1Session methods only return unicode strings. #55.
- Renamed requests_oauthlib.core to requests_oauthlib.oauth1_auth for consistency. #79.
- Added Facebook compliance fix and access_token_response hook to OAuth2Session. #63.
- Added LinkedIn compliance fix.
- Added refresh_token_response compliance hook, invoked before parsing the refresh token.
- Correctly limit compliance hooks to running only once!
- Content type guessing should only be done when no content type is given
- OAuth1 now updates r.headers instead of replacing it with non case insensitive dict
- Remove last use of Response.content (in OAuth1Session). #44.
- State param can now be supplied in OAuth2Session.authorize_url
