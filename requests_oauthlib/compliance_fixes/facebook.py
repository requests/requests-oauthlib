from json import dumps
from oauthlib.common import urldecode


def facebook_compliance_fix(session):

    def _compliance_fix(r):
        # Facebook returns urlencoded token, or json on error. Skip
        # compliance fix if we can't urldecode.
        try:
            token = dict(urldecode(r.text))
        except ValueError:
            return r

        expires = token.get('expires')
        if expires is not None:
            token['expires_in'] = expires
        token['token_type'] = 'Bearer'
        r._content = dumps(token)
        return r

    session.register_compliance_hook('access_token_response', _compliance_fix)
    return session
