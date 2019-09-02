from json import loads, dumps

from oauthlib.common import to_unicode


def linkedin_compliance_fix(session):
    def _missing_token_type(r):
        token = loads(r.text)
        token["token_type"] = "Bearer"
        r._content = to_unicode(dumps(token)).encode("UTF-8")
        return r

    session.register_compliance_hook("access_token_response", _missing_token_type)
    return session
