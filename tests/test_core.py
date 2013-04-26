# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mock
import sys
import requests
import requests_oauthlib
try:
    from io import StringIO # python 3
except ImportError:
    from StringIO import StringIO # python 2
import unittest

if sys.version[0] == '3':
    bytes_type = bytes
else:
    bytes_type = str


@mock.patch('oauthlib.oauth1.rfc5849.generate_timestamp')
@mock.patch('oauthlib.oauth1.rfc5849.generate_nonce')
class OAuth1Test(unittest.TestCase):

    def setUp(self):
        def converting_equals(a, b):
            if isinstance(a, bytes_type):
                a = a.decode('utf-8')
            if isinstance(b, bytes_type):
                b = b.decode('utf-8')
            self.assertEquals(a, b)

        self.assertEqual = converting_equals

    def testFormEncoded(self, generate_nonce, generate_timestamp):
        """OAuth1 assumes form encoded if content type is not specified."""
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '1'
        oauth = requests_oauthlib.OAuth1('client_key')
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        r = requests.Request(method='POST', url='http://a.b/path?query=retain',
                auth=oauth, data='this=really&is=&+form=encoded', headers=headers)
        a = r.prepare()

        self.assertEqual(a.url, 'http://a.b/path?query=retain')
        self.assertEqual(a.body, 'this=really&is=&+form=encoded')
        self.assertEqual(a.headers.get('Content-Type'.encode('utf-8')), 'application/x-www-form-urlencoded')

        # guess content-type
        r = requests.Request(method='POST', url='http://a.b/path?query=retain',
                auth=oauth, data='this=really&is=&+form=encoded')
        b = r.prepare()
        self.assertEqual(b.url, 'http://a.b/path?query=retain')
        self.assertEqual(b.body, 'this=really&is=&+form=encoded')
        self.assertEqual(b.headers.get('Content-Type'.encode('utf-8')), 'application/x-www-form-urlencoded')

        self.assertEqual(a.headers.get('Authorization'.encode('utf-8')),
                b.headers.get('Authorization'.encode('utf-8')))

    def testNonFormEncoded(self, generate_nonce, generate_timestamp):
        """OAuth signature only depend on body if it is form encoded."""
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '1'
        oauth = requests_oauthlib.OAuth1('client_key')

        r = requests.Request(method='POST', url='http://a.b/path?query=retain',
                auth=oauth, data='this really is not form encoded')
        a = r.prepare()

        r = requests.Request(method='POST', url='http://a.b/path?query=retain',
                auth=oauth)
        b = r.prepare()

        self.assertEqual(a.headers.get('Authorization'),
                b.headers.get('Authorization'))

        r = requests.Request(method='POST', url='http://a.b/path?query=retain',
                auth=oauth, files={'test': StringIO('hello')})
        c = r.prepare()

        self.assertEqual(b.headers.get('Authorization'),
                c.headers.get('Authorization'))

    def testNoUnicodeInAuthorizationHeader(self, generate_nonce, generate_timestamp):
        """
        If we have an unicode Authorization key or value, httplib will raise an
        UnicodeDecodeError in _send_output
        """
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '1'
        r = requests.Request(
            method='POST',
            url='http://a.b',
            files={'test': StringIO(u'é')},
            auth=requests_oauthlib.OAuth1("client_key")
        ).prepare()
        for key, value in r.headers.items():
            if key == "Authorization":
                self.assertTrue(isinstance(key, bytes_type))
                self.assertTrue(isinstance(value, bytes_type))
