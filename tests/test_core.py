# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mock
import sys
import requests
import requests_oauthlib
import oauthlib
import os.path
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
        self.assertEqual(a.headers.get('Content-Type'), 'application/x-www-form-urlencoded')

        # guess content-type
        r = requests.Request(method='POST', url='http://a.b/path?query=retain',
                auth=oauth, data='this=really&is=&+form=encoded')
        b = r.prepare()
        self.assertEqual(b.url, 'http://a.b/path?query=retain')
        self.assertEqual(b.body, 'this=really&is=&+form=encoded')
        self.assertEqual(b.headers.get('Content-Type'), 'application/x-www-form-urlencoded')

        self.assertEqual(a.headers.get('Authorization'),
                b.headers.get('Authorization'))

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

    def testCanPostBinaryData(self, generate_nonce, generate_timestamp):
        """
        Test we can post binary data. Should prevent regression of the
        UnicodeDecodeError issue.
        """
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '1'
        oauth = requests_oauthlib.OAuth1('client_key')
        dirname = os.path.dirname(__file__)
        fname = os.path.join(dirname, 'test.bin')

        with open(fname, 'rb') as f:
            r = requests.post('http://httpbin.org/post', data={'hi': 'there'},
                              files={'media': (os.path.basename(f.name), f)},
                                headers={'content-type':'application/octet-stream'},
                              auth=oauth)
            self.assertEqual(r.status_code, 200)

    def test_url_is_native_str(self, generate_nonce, generate_timestamp):
        """
        Test that the URL is always a native string.
        """
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '1'
        oauth = requests_oauthlib.OAuth1('client_key')

        r = requests.get('http://httpbin.org/get', auth=oauth)
        self.assertTrue(isinstance(r.request.url, str))

    def test_content_type_override(self, generate_nonce, generate_timestamp):
        """
        Content type should only be guessed if none is given.
        """
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '1'
        oauth = requests_oauthlib.OAuth1('client_key')
        data = 'a'
        r = requests.post('http://httpbin.org/get', data=data, auth=oauth)
        self.assertEqual(r.request.headers.get('Content-Type'),
                         'application/x-www-form-urlencoded')
        r = requests.post('http://httpbin.org/get', auth=oauth, data=data,
                          headers={'Content-type': 'application/json'})
        self.assertEqual(r.request.headers.get('Content-Type'),
                         'application/json')


    def test_register_client_class(self, generate_timestamp, generate_nonce):
        class ClientSubclass(oauthlib.oauth1.Client):
            pass

        self.assertTrue(hasattr(requests_oauthlib.OAuth1, 'client_class'))

        self.assertEqual(
            requests_oauthlib.OAuth1.client_class,
            oauthlib.oauth1.Client)

        normal = requests_oauthlib.OAuth1('client_key')

        self.assertTrue(isinstance(normal.client, oauthlib.oauth1.Client))
        self.assertFalse(isinstance(normal.client, ClientSubclass))

        requests_oauthlib.OAuth1.client_class = ClientSubclass

        self.assertEqual(requests_oauthlib.OAuth1.client_class, ClientSubclass)

        custom = requests_oauthlib.OAuth1('client_key')

        self.assertTrue(isinstance(custom.client, oauthlib.oauth1.Client))
        self.assertTrue(isinstance(custom.client, ClientSubclass))

        overridden = requests_oauthlib.OAuth1('client_key',
            client_class = oauthlib.oauth1.Client)

        self.assertTrue(isinstance(overridden.client, oauthlib.oauth1.Client))
        self.assertFalse(isinstance(normal.client, ClientSubclass))
