History
-------

v0.5.0 (4 May 2015)
+++++++++++++++++++
- Fix ``TypeError`` being raised instead of ``TokenMissing`` error.
- Raise requests exceptions on 4XX and 5XX responses in the OAuth2 flow.
- Avoid ``AttributeError`` when initializing the ``OAuth2Session`` class
  without complete client information.

v0.4.2
++++++
- New ``authorized`` property on OAuth1Session and OAuth2Session, which allows
  you to easily determine if the session is already authorized with OAuth tokens
  or not.
- New ``TokenMissing`` and ``VerifierMissing`` exception classes for OAuth1Session:
  this will make it easier to catch and identify these exceptions.

v0.4.1 (6 June 2014)
++++++++++++++++++++
- New install target ``[rsa]`` for people using OAuth1 RSA-SHA1 signature
  method.
- Fixed bug in OAuth2 where supplied state param was not used in auth url.
- OAuth2 HTTPS checking can be disabled by setting environment variable
  ``OAUTHLIB_INSECURE_TRANSPORT``.
- OAuth1 now re-authorize upon redirects.
- OAuth1 token fetching now raise a detailed error message when the
  response body is incorrectly encoded or the request was denied.
- Added support for custom OAuth1 clients.
- OAuth2 compliance fix for Sina Weibo.
- Multiple fixes to facebook compliance fix.
- Compliance fixes now re-encode body properly as bytes in Python 3.
- Logging now properly done under ``requests_oauthlib`` namespace instead
  of piggybacking on oauthlib namespace.
- Logging introduced for OAuth1 auth and session.

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
