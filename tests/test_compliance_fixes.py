from __future__ import unicode_literals
import unittest

import mock
import requests

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
from requests_oauthlib.compliance_fixes import weibo_compliance_fix


class FacebookComplianceFixTest(unittest.TestCase):

    def test_fetch_access_token(self):
        facebook = OAuth2Session('foo', redirect_uri='https://i.b')
        facebook = facebook_compliance_fix(facebook)

        facebook.post = mock.MagicMock()
        response = requests.Response()
        response.status_code = 200
        response.request = mock.MagicMock()
        response._content = 'access_token=urlencoded'.encode('UTF-8')
        response.headers['Content-Type'] = 'text/plain'
        facebook.post.return_value = response

        token = facebook.fetch_token('https://mocked.out',
                                     client_secret='bar',
                                     authorization_response='https://i.b/?code=hello')
        self.assertEqual(token, {'access_token': 'urlencoded', 'token_type': 'Bearer'})


class LinkedInComplianceFixTest(unittest.TestCase):

    def test_fetch_access_token(self):
        linkedin = OAuth2Session('foo', redirect_uri='https://i.b')
        linkedin = linkedin_compliance_fix(linkedin)

        linkedin.post = mock.MagicMock()
        response = requests.Response()
        response.status_code = 200
        response.request = mock.MagicMock()
        response._content = '{"access_token":"linkedin"}'.encode('UTF-8')
        linkedin.post.return_value = response

        token = linkedin.fetch_token('https://mocked.out',
                                     client_secret='bar',
                                     authorization_response='https://i.b/?code=hello')
        self.assertEqual(token, {'access_token': 'linkedin', 'token_type': 'Bearer'})


class WeiboComplianceFixTest(unittest.TestCase):

    def test_fetch_access_token(self):
        weibo = OAuth2Session('foo', redirect_uri='https://i.b')
        weibo = weibo_compliance_fix(weibo)

        weibo.post = mock.MagicMock()
        response = requests.Response()
        response.status_code = 200
        response.request = mock.MagicMock()
        response._content = '{"access_token":"weibo"}'.encode('UTF-8')
        weibo.post.return_value = response

        token = weibo.fetch_token('https://mocked.out',
                                     client_secret='bar',
                                     authorization_response='https://i.b/?code=hello')
        self.assertEqual(token, {'access_token': 'weibo', 'token_type': 'Bearer'})

