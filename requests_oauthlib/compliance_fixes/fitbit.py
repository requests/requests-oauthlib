import base64

from oauthlib.common import add_params_to_uri


def fitbit_compliance_fix(session, client_secret):
    def _non_compliant_auth_header(url, headers, body):
        basic_auth_value = "{}:{}".format(session._client.client_id, client_secret)
        headers["Authorization"] = 'Basic {}'.format(base64.b64encode(basic_auth_value))
        token = [('token', session._client.access_token)]
        url = add_params_to_uri(url, token)
        return url, headers, body

    session.register_compliance_hook('refresh_token_request', _non_compliant_auth_header)
    return session
