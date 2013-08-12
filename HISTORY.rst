History
-------

v0.4.0dev
+++++++++
- OAuth1Session methods only return unicode strings. #55.
- Added facebook compliance fix and access_token_response hook to OAuth2Session. #63.
- Content type guessing should only be done when no content type is given
- OAuth1 now updates r.headers instead of replacing it with non case insensitive dict
- Remove last use of Response.content (in OAuth1Session). #44.
