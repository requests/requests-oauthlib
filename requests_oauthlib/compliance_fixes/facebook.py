from json import dumps
from oauthlib.common import urldecode
from urllib import parse_qsl


def facebook_compliance_fix(session):

    def _compliance_fix(r):
        # if Facebook claims to be sending us json, let's trust them.
        if r.headers['content-type'] == 'application/json':
            return r

        # Facebook returns a content-type of text/plain when sending their
        # x-www-form-urlencoded responses, along with a 200. If not, let's
        # assume we're getting JSON and bail on the fix.
        if r.headers['content-type'] == 'text/plain' and r.status_code == 200:
            token = dict(parse_qsl(r.text, keep_blank_values=True))
        else:
            return r

        expires = token.get('expires')
        if expires is not None:
            token['expires_in'] = expires
        token['token_type'] = 'Bearer'
        r._content = dumps(token)
        return r

    session.register_compliance_hook('access_token_response', _compliance_fix)
    return session
