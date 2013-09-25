# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from oauthlib.common import extract_params
from oauthlib.oauth1 import (Client, SIGNATURE_HMAC, SIGNATURE_TYPE_AUTH_HEADER)

CONTENT_TYPE_FORM_URLENCODED = 'application/x-www-form-urlencoded'
CONTENT_TYPE_MULTI_PART = 'multipart/form-data'

import sys
if sys.version > "3":
    unicode = str

    def to_native_str(string):
        return string.decode('utf-8')
else:
    def to_native_str(string):
        return string

# OBS!: Correct signing of requests are conditional on invoking OAuth1
# as the last step of preparing a request, or at least having the
# content-type set properly.
class OAuth1(object):
    """Signs the request using OAuth 1 (RFC5849)"""
    def __init__(self, client_key,
            client_secret=None,
            resource_owner_key=None,
            resource_owner_secret=None,
            callback_uri=None,
            signature_method=SIGNATURE_HMAC,
            signature_type=SIGNATURE_TYPE_AUTH_HEADER,
            rsa_key=None, verifier=None,
            decoding='utf-8'):

        try:
            signature_type = signature_type.upper()
        except AttributeError:
            pass

        self.client = Client(client_key, client_secret, resource_owner_key,
            resource_owner_secret, callback_uri, signature_method,
            signature_type, rsa_key, verifier, decoding=decoding)

    def __call__(self, r):
        """Add OAuth parameters to the request.

        Parameters may be included from the body if the content-type is
        urlencoded, if no content type is set a guess is made.
        """
        # Overwriting url is safe here as request will not modify it past
        # this point.

        content_type = r.headers.get('Content-Type', '')
        if not content_type and extract_params(r.body):
            content_type = CONTENT_TYPE_FORM_URLENCODED
        if not isinstance(content_type, unicode):
            content_type = content_type.decode('utf-8')

        is_form_encoded = (CONTENT_TYPE_FORM_URLENCODED in content_type)

        if is_form_encoded:
            r.headers['Content-Type'] = CONTENT_TYPE_FORM_URLENCODED
            r.url, headers, r.body = self.client.sign(
                unicode(r.url), unicode(r.method), r.body or '', r.headers)
        else:
            # Omit body data in the signing of non form-encoded requests
            r.url, headers, _ = self.client.sign(
                unicode(r.url), unicode(r.method), None, r.headers)

        r.prepare_headers(headers)
        r.url = to_native_str(r.url)
        return r
