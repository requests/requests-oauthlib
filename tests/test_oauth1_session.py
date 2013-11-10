from __future__ import unicode_literals
import mock
import unittest
import sys

from oauthlib.oauth1 import SIGNATURE_TYPE_QUERY, SIGNATURE_TYPE_BODY
from oauthlib.oauth1 import SIGNATURE_RSA, SIGNATURE_PLAINTEXT
from requests_oauthlib import OAuth1Session

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

if sys.version[0] == '3':
    unicode_type = str
    bytes_type = bytes
else:
    unicode_type = unicode
    bytes_type = str


class OAuth1SessionTest(unittest.TestCase):

    def setUp(self):
        # For python 2.6
        if not hasattr(self, 'assertIn'):
            self.assertIn = lambda a, b: self.assertTrue(a in b)

    def test_signature_types(self):
        def verify_signature(getter):
            def fake_send(r, **kwargs):
                signature = getter(r)
                if isinstance(signature, bytes_type):
                    signature = signature.decode('utf-8')
                self.assertIn('oauth_signature', signature)
                resp = mock.MagicMock()
                resp.cookes = []
                return resp
            return fake_send

        header = OAuth1Session('foo')
        header.send = verify_signature(lambda r: r.headers['Authorization'])
        header.post('https://i.b')

        query = OAuth1Session('foo', signature_type=SIGNATURE_TYPE_QUERY)
        query.send = verify_signature(lambda r: r.url)
        query.post('https://i.b')

        body = OAuth1Session('foo', signature_type=SIGNATURE_TYPE_BODY)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body.send = verify_signature(lambda r: r.body)
        body.post('https://i.b', headers=headers, data='')

    @mock.patch('oauthlib.oauth1.rfc5849.generate_timestamp')
    @mock.patch('oauthlib.oauth1.rfc5849.generate_nonce')
    def test_signature_methods(self, generate_nonce, generate_timestamp):
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '123'

        signature = 'OAuth oauth_nonce="abc", oauth_timestamp="123", oauth_version="1.0", oauth_signature_method="HMAC-SHA1", oauth_consumer_key="foo", oauth_signature="h2sRqLArjhlc5p3FTkuNogVHlKE%3D"'
        auth = OAuth1Session('foo')
        auth.send = self.verify_signature(signature)
        auth.post('https://i.b')

        signature = 'OAuth oauth_nonce="abc", oauth_timestamp="123", oauth_version="1.0", oauth_signature_method="PLAINTEXT", oauth_consumer_key="foo", oauth_signature="%26"'
        auth = OAuth1Session('foo', signature_method=SIGNATURE_PLAINTEXT)
        auth.send = self.verify_signature(signature)
        auth.post('https://i.b')

        rsa_key = ("-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEogIBAAKCAQEApF1JaMSN8TEsh4N4O/5SpEAVLivJyLH+Cgl3OQBPGgJkt8cg\n"
            "49oasl+5iJS+VdrILxWM9/JCJyURpUuslX4Eb4eUBtQ0x5BaPa8+S2NLdGTaL7nB\n"
            "OO8o8n0C5FEUU+qlEip79KE8aqOj+OC44VsIquSmOvWIQD26n3fCVlgwoRBD1gzz\n"
            "sDOeaSyzpKrZR851Kh6rEmF2qjJ8jt6EkxMsRNACmBomzgA4M1TTsisSUO87444p\n"
            "e35Z4/n5c735o2fZMrGgMwiJNh7rT8SYxtIkxngioiGnwkxGQxQ4NzPAHg+XSY0J\n"
            "04pNm7KqTkgtxyrqOANJLIjXlR+U9SQ90NjHVQIDAQABAoIBABuBPOKaWcJt3yzC\n"
            "NGGduoif7KtwSnEaUA+v69KPGa2Zju8uFHPssKD+4dZYRc2qMeunKJLpaGaSjnRh\n"
            "yHyvvOBJCN1nr3lhz6gY5kzJTfwpUFXCOPJlGy4Q+2Xnp4YvcvYqQ9n5DVovDiZ8\n"
            "vJOBn16xqpudMPLHIa7D5LJ8SY76HBjE+imTXw1EShdh5TOV9bmPFQqH6JFzowRH\n"
            "hyH2DPHuyHJj6cl8FyqJw5lVWzG3n6Prvk7bYHsjmGjurN35UsumNAp6VouNyUP1\n"
            "RAEcUJega49aIs6/FJ0ENJzQjlsAzVbTleHkpez2aIok+wsWJGJ4SVxAjADOWAaZ\n"
            "uEJPc3UCgYEA1g4ZGrXOuo75p9/MRIepXGpBWxip4V7B9XmO9WzPCv8nMorJntWB\n"
            "msYV1I01aITxadHatO4Gl2xLniNkDyrEQzJ7w38RQgsVK+CqbnC0K9N77QPbHeC1\n"
            "YQd9RCNyUohOimKvb7jyv798FBU1GO5QI2eNgfnnfteSVXhD2iOoTOsCgYEAxJJ+\n"
            "8toxJdnLa0uUsAbql6zeNXGbUBMzu3FomKlyuWuq841jS2kIalaO/TRj5hbnE45j\n"
            "mCjeLgTVO6Ach3Wfk4zrqajqfFJ0zUg/Wexp49lC3RWiV4icBb85Q6bzeJD9Dn9v\n"
            "hjpfWVkczf/NeA1fGH/pcgfkT6Dm706GFFttLL8CgYBl/HeXk1H47xAiHO4dJKnb\n"
            "v0B+X8To/RXamF01r+8BpUoOubOQetdyX7ic+d6deuHu8i6LD/GSCeYJZYFR/KVg\n"
            "AtiW757QYalnq3ZogkhFrVCZP8IRfTPOFBxp752TlyAcrSI7T9pQ47IBe4094KXM\n"
            "CJWSfPgAJkOxd0iU0XJpmwKBgGfQxuMTgSlwYRKFlD1zKap5TdID8fbUbVnth0Q5\n"
            "GbH7vwlp/qrxCdS/aj0n0irOpbOaW9ccnlrHiqY25VpVMLYIkt3DrDOEiNNx+KNR\n"
            "TItdTwbcSiTYrS4L0/56ydM/H6bsfsXxRjI18hSJqMZiqXqS84OZz2aOn+h7HCzc\n"
            "LEiZAoGASk20wFvilpRKHq79xxFWiDUPHi0x0pp82dYIEntGQkKUWkbSlhgf3MAi\n"
            "5NEQTDmXdnB+rVeWIvEi+BXfdnNgdn8eC4zSdtF4sIAhYr5VWZo0WVWDhT7u2ccv\n"
            "ZBFymiz8lo3gN57wGUCi9pbZqzV1+ZppX6YTNDdDCE0q+KO3Cec=\n"
            "-----END RSA PRIVATE KEY-----")
        signature = 'OAuth oauth_nonce="abc", oauth_timestamp="123", oauth_version="1.0", oauth_signature_method="RSA-SHA1", oauth_consumer_key="foo", oauth_signature="j8WF8PGjojT82aUDd2EL%2Bz7HCoHInFzWUpiEKMCy%2BJ2cYHWcBS7mXlmFDLgAKV0P%2FyX4TrpXODYnJ6dRWdfghqwDpi%2FlQmB2jxCiGMdJoYxh3c5zDf26gEbGdP6D7OSsp5HUnzH6sNkmVjuE%2FxoJcHJdc23H6GhOs7VJ2LWNdbhKWP%2FMMlTrcoQDn8lz%2Fb24WsJ6ae1txkUzpFOOlLM8aTdNtGL4OtsubOlRhNqnAFq93FyhXg0KjzUyIZzmMX9Vx90jTks5QeBGYcLE0Op2iHb2u%2FO%2BEgdwFchgEwE5LgMUyHUI4F3Wglp28yHOAMjPkI%2FkWMvpxtMrU3Z3KN31WQ%3D%3D"'
        auth = OAuth1Session('foo', signature_method=SIGNATURE_RSA,
                             rsa_key=rsa_key)
        auth.send = self.verify_signature(signature)
        auth.post('https://i.b')

    @mock.patch('oauthlib.oauth1.rfc5849.generate_timestamp')
    @mock.patch('oauthlib.oauth1.rfc5849.generate_nonce')
    def test_binary_upload(self, generate_nonce, generate_timestamp):
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '123'
        fake_xml = StringIO('hello world')
        headers = {'Content-Type': 'application/xml'}
        signature = 'OAuth oauth_nonce="abc", oauth_timestamp="123", oauth_version="1.0", oauth_signature_method="HMAC-SHA1", oauth_consumer_key="foo", oauth_signature="h2sRqLArjhlc5p3FTkuNogVHlKE%3D"'
        auth = OAuth1Session('foo')
        auth.send = self.verify_signature(signature)
        auth.post('https://i.b', headers=headers, files=[('fake', fake_xml)])

    @mock.patch('oauthlib.oauth1.rfc5849.generate_timestamp')
    @mock.patch('oauthlib.oauth1.rfc5849.generate_nonce')
    def test_nonascii(self, generate_nonce, generate_timestamp):
        generate_nonce.return_value = 'abc'
        generate_timestamp.return_value = '123'
        signature = 'OAuth oauth_nonce="abc", oauth_timestamp="123", oauth_version="1.0", oauth_signature_method="HMAC-SHA1", oauth_consumer_key="foo", oauth_signature="W0haoue5IZAZoaJiYCtfqwMf8x8%3D"'
        auth = OAuth1Session('foo')
        auth.send = self.verify_signature(signature)
        auth.post('https://i.b?cjk=%E5%95%A6%E5%95%A6')

    def test_authorization_url(self):
        auth = OAuth1Session('foo')
        url = 'https://example.comm/authorize'
        token = 'asluif023sf'
        auth_url = auth.authorization_url(url, request_token=token)
        self.assertEqual(auth_url, url + '?oauth_token=' + token)

    def test_parse_response_url(self):
        url = 'https://i.b/callback?oauth_token=foo&oauth_verifier=bar'
        auth = OAuth1Session('foo')
        resp = auth.parse_authorization_response(url)
        self.assertEqual(resp['oauth_token'], 'foo')
        self.assertEqual(resp['oauth_verifier'], 'bar')
        for k, v in resp.items():
            self.assertTrue(isinstance(k, unicode_type))
            self.assertTrue(isinstance(v, unicode_type))

    def test_fetch_request_token(self):
        auth = OAuth1Session('foo')
        auth.send = self.fake_body('oauth_token=foo')
        resp = auth.fetch_request_token('https://example.com/token')
        self.assertEqual(resp['oauth_token'], 'foo')
        for k, v in resp.items():
            self.assertTrue(isinstance(k, unicode_type))
            self.assertTrue(isinstance(v, unicode_type))

    def test_fetch_access_token(self):
        auth = OAuth1Session('foo', verifier='bar')
        auth.send = self.fake_body('oauth_token=foo')
        resp = auth.fetch_access_token('https://example.com/token')
        self.assertEqual(resp['oauth_token'], 'foo')
        for k, v in resp.items():
            self.assertTrue(isinstance(k, unicode_type))
            self.assertTrue(isinstance(v, unicode_type))

    def test_params_with_spaces(self):
        class RequestIntercepter(OAuth1Session):
            def send(self, request, **kwargs):
                self.sent_url = request.url

        auth = RequestIntercepter('foo')
        auth.get('http://example.com/', params={'q': 'foo bar'})
        self.assertEqual(str('http://example.com/?q=foo%20bar'), auth.sent_url)

    def verify_signature(self, signature):
        def fake_send(r, **kwargs):
            auth_header = r.headers['Authorization']
            if isinstance(auth_header, bytes_type):
                auth_header = auth_header.decode('utf-8')
            self.assertEqual(auth_header, signature)
            resp = mock.MagicMock()
            resp.cookes = []
            return resp
        return fake_send

    def fake_body(self, body):
        def fake_send(r, **kwargs):
            resp = mock.MagicMock()
            resp.cookes = []
            resp.text = body
            return resp
        return fake_send
