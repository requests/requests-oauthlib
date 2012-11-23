# -*- coding: utf-8 -*-

from oauthlib.oauth1 import rfc5849
from oauthlib.common import extract_params
from oauthlib.oauth1.rfc5849 import (Client, SIGNATURE_HMAC, SIGNATURE_TYPE_AUTH_HEADER)

CONTENT_TYPE_FORM_URLENCODED = 'application/x-www-form-urlencoded'
CONTENT_TYPE_MULTI_PART = 'multipart/form-data'


class OAuth1(object):
    """Signs the request using OAuth 1 (RFC5849)"""
    def __init__(self, client_key,
            client_secret=None,
            resource_owner_key=None,
            resource_owner_secret=None,
            callback_uri=None,
            signature_method=SIGNATURE_HMAC,
            signature_type=SIGNATURE_TYPE_AUTH_HEADER,
            rsa_key=None, verifier=None):

        try:
            signature_type = signature_type.upper()
        except AttributeError:
            pass

        self.client = Client(client_key, client_secret, resource_owner_key,
            resource_owner_secret, callback_uri, signature_method,
            signature_type, rsa_key, verifier)

    def __call__(self, r):
        """Add OAuth parameters to the request.

        Parameters may be included from the body if the content-type is
        urlencoded, if no content type is set an educated guess is made.
        """
        # split(";") because Content-Type may be "multipart/form-data; boundary=xxxxx"
        contenttype = r.headers.get('Content-Type', '').split(";")[0].lower()
        # extract_params will not give params unless the body is a properly
        # formatted string, a dictionary or a list of 2-tuples.
        decoded_body = extract_params(r.data)

        # extract_params can only check the present r.data and does not know
        # of r.files, thus an extra check is performed. We know that
        # if files are present the request will not have
        # Content-type: x-www-form-urlencoded. We guess it will have
        # a mimetype of multipart/form-data and if this is not the case
        # we assume the correct header will be set later.
        _oauth_signed = True
        if r.files and contenttype == CONTENT_TYPE_MULTI_PART:
            # Omit body data in the signing and since it will always
            # be empty (cant add paras to body if multipart) and we wish
            # to preserve body.
            r.url, r.headers, _ = self.client.sign(
                unicode(r.full_url), unicode(r.method), None, r.headers)
        elif decoded_body is not None and contenttype in (CONTENT_TYPE_FORM_URLENCODED, ''):
            # Normal signing
            if not contenttype:
                r.headers['Content-Type'] = CONTENT_TYPE_FORM_URLENCODED
            r.url, r.headers, r.data = self.client.sign(
                unicode(r.full_url), unicode(r.method), r.data, r.headers)
        else:
            _oauth_signed = False
        if _oauth_signed:
            # Both flows add params to the URL by using r.full_url,
            # so this prevents adding it again later
            r.params = {}

            # Having the authorization header, key or value, in unicode will
            # result in UnicodeDecodeErrors when the request is concatenated
            # by httplib. This can easily be seen when attaching files.
            # Note that simply encoding the value is not enough since Python
            # saves the type of first key set. Thus we remove and re-add.
            # >>> d = {u'a':u'foo'}
            # >>> d['a'] = 'foo'
            # >>> d
            # { u'a' : 'foo' }
            u_header = unicode('Authorization')
            if u_header in r.headers:
                auth_header = r.headers[u_header].encode('utf-8')
                del r.headers[u_header]
                r.headers['Authorization'] = auth_header

        return r