from oauthlib.common import add_params_to_uri


def slack_compliance_fix(session):
    def _non_compliant_param_name(url, headers, data):
        token = [('token', session._client.access_token)]
        url = add_params_to_uri(url, token)
        return url, headers, data

    session.register_compliance_hook('protected_request', _non_compliant_param_name)
    return session
