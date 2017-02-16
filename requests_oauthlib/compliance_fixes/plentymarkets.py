from json import dumps, loads

from oauthlib.common import to_unicode


def plentymarkets_compliance_fix(session):

    def _compliance_fix(r):

        # Plenty returns the Token in CamelCase instead with _
        if 'application/json' in r.headers.get('content-type', {}) and r.status_code == 200:
            token = loads(r.text)
        else:
            return r

        expires = token.pop('expiresIn')
        if expires is not None:
            token['expires_in'] = expires

        access_token = token.pop('accessToken')
        if access_token is not None:
            token['access_token'] = access_token

        refresh_token = token.pop('refreshToken')
        if refresh_token is not None:
            token['refresh_token'] = refresh_token

        token['token_type'] = 'Bearer'
        del token['tokenType']

        r._content = to_unicode(dumps(token)).encode('UTF-8')
        return r

    session.register_compliance_hook('access_token_response', _compliance_fix)
    return session
