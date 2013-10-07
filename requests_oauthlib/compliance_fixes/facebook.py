from json import dumps
from oauthlib.common import urldecode

import six

def facebook_compliance_fix(session):

    def _compliance_fix(r):
        token = dict(urldecode(r.text))
        expires = token.get('expires')
        if expires is not None:
            token['expires_in'] = expires
        token['token_type'] = 'Bearer'
        r._content = dumps(token)

        # on Python 3 this may raise an exception, since requests' text
        # property expects a bytes object instead of str.
        if not isinstance(r._content, six.binary_type):
            r._content = r._content.encode('utf-8')

        return r

    session.register_compliance_hook('access_token_response', _compliance_fix)
    return session
