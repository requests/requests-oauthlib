import json
from oauthlib.common import to_unicode


def ebay_compliance_fix(session):
    def _compliance_fix(response):
        token = json.loads(response.content)

        # eBay responds with non-compliant token types.
        # https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html
        # https://developer.ebay.com/api-docs/static/oauth-auth-code-grant-request.html
        # Modify these to be "Bearer".
        if token["token_type"] in ["Application Access Token", "User Access Token"]:
            token["token_type"] = "Bearer"
            fixed_token = json.dumps(token)
            response._content = to_unicode(fixed_token).encode("utf-8")

        return response

    session.register_compliance_hook("access_token_response", _compliance_fix)
    session.register_compliance_hook("refresh_token_response", _compliance_fix)

    return session
