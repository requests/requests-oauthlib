import json
from oauthlib.common import urldecode

"""
Wix requires the request body for token requests to be sent in JSON format
instead of x-www-form-urlencoded.
"""
def wix_compliance_fix(session):

    def _non_compliant_access_token_request_body(
            url: str, headers: dict, request_kwargs: dict
    ):
        """
        Move the request body from the `data` kwarg to the `json` kwarg,
        and set the `Content-Type` header to `application/json`.
        """
        headers["Content-Type"] = "application/json"
        request_kwargs["json"] = request_kwargs["data"]
        del request_kwargs["data"]
        return url, headers, request_kwargs

    def _non_compliant_refresh_token_request_body(
            token_url: str, headers: dict, body: str
    ):
        """
        Convert the body from a urlencoded string to a JSON string,
        and set the `Content-Type` header to `application/json`.
        """
        headers["Content-Type"] = "application/json"
        body = json.dumps(dict(urldecode(body)))
        return token_url, headers, body

    session.register_compliance_hook("access_token_request", _non_compliant_access_token_request_body)
    session.register_compliance_hook("refresh_token_request", _non_compliant_refresh_token_request_body)

    return session
