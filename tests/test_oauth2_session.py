from __future__ import unicode_literals
import json
import mock
import time
from copy import deepcopy
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from oauthlib.common import urlencode
from oauthlib.oauth2 import TokenExpiredError, OAuth2Error
from oauthlib.oauth2 import MismatchingStateError
from oauthlib.oauth2 import WebApplicationClient, MobileApplicationClient
from oauthlib.oauth2 import LegacyApplicationClient, BackendApplicationClient
from requests_oauthlib import OAuth2Session, TokenUpdated


fake_time = time.time()



def fake_token(token):
    def fake_send(r, **kwargs):
        resp = mock.MagicMock()
        resp.text = json.dumps(token)
        return resp
    return fake_send


class OAuth2SessionTest(TestCase):

    def setUp(self):
        # For python 2.6
        if not hasattr(self, 'assertIn'):
            self.assertIn = lambda a, b: self.assertTrue(a in b)

        self.token = {
            'token_type': 'Bearer',
            'access_token': 'asdfoiw37850234lkjsdfsdf',
            'refresh_token': 'sldvafkjw34509s8dfsdf',
            'expires_in': '3600',
            'expires_at': fake_time + 3600,
        }
        self.client_id = 'foo'
        self.clients = [
            WebApplicationClient(self.client_id, code='asdf345xdf'),
            LegacyApplicationClient(self.client_id),
            BackendApplicationClient(self.client_id),
        ]
        self.all_clients = self.clients + [MobileApplicationClient(self.client_id)]

    def test_add_token(self):
        token = 'Bearer ' + self.token['access_token']

        def verifier(r, **kwargs):
            auth_header = r.headers.get('Authorization', None)
            if 'Authorization'.encode('utf-8') in r.headers:
                auth_header = r.headers['Authorization'.encode('utf-8')]
            self.assertEqual(auth_header, token)
            resp = mock.MagicMock()
            resp.cookes = []
            return resp

        for client in self.all_clients:
            auth = OAuth2Session(client=client, token=self.token)
            auth.send = verifier
            auth.get('https://i.b')

    def test_authorization_url(self):
        url = 'https://example.com/authorize?foo=bar'

        web = WebApplicationClient(self.client_id)
        s = OAuth2Session(client=web)
        auth_url, state = s.authorization_url(url)
        self.assertIn(state, auth_url)
        self.assertIn(self.client_id, auth_url)
        self.assertIn('response_type=code', auth_url)

        mobile = MobileApplicationClient(self.client_id)
        s = OAuth2Session(client=mobile)
        auth_url, state = s.authorization_url(url)
        self.assertIn(state, auth_url)
        self.assertIn(self.client_id, auth_url)
        self.assertIn('response_type=token', auth_url)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_refresh_token_request(self):
        self.expired_token = dict(self.token)
        self.expired_token['expires_in'] = '-1'
        del self.expired_token['expires_at']

        def fake_refresh(r, **kwargs):
            resp = mock.MagicMock()
            resp.text = json.dumps(self.token)
            return resp

        # No auto refresh setup
        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.expired_token)
            self.assertRaises(TokenExpiredError, auth.get, 'https://i.b')

        # Auto refresh but no auto update
        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.expired_token,
                    auto_refresh_url='https://i.b/refresh')
            auth.send = fake_refresh
            self.assertRaises(TokenUpdated, auth.get, 'https://i.b')

        # Auto refresh and auto update
        def token_updater(token):
            self.assertEqual(token, self.token)

        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.expired_token,
                    auto_refresh_url='https://i.b/refresh',
                    token_updater=token_updater)
            auth.send = fake_refresh
            auth.get('https://i.b')

    @mock.patch("time.time", new=lambda: fake_time)
    def test_token_from_fragment(self):
        mobile = MobileApplicationClient(self.client_id)
        response_url = 'https://i.b/callback#' + urlencode(self.token.items())
        auth = OAuth2Session(client=mobile)
        self.assertEqual(auth.token_from_fragment(response_url), self.token)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_fetch_token(self):
        url = 'https://example.com/token'

        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.token)
            auth.send = fake_token(self.token)
            self.assertEqual(auth.fetch_token(url), self.token)

        error = {'error': 'invalid_request'}
        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.token)
            auth.send = fake_token(error)
            self.assertRaises(OAuth2Error, auth.fetch_token, url)

    def test_cleans_previous_token_before_fetching_new_one(self):
        """Makes sure the previous token is cleaned before fetching a new one.

        The reason behind it is that, if the previous token is expired, this
        method shouldn't fail with a TokenExpiredError, since it's attempting
        to get a new one (which shouldn't be expired).

        """
        new_token = deepcopy(self.token)
        past = time.time() - 7200
        now = time.time()
        self.token['expires_at'] = past
        new_token['expires_at'] = now + 3600
        url = 'https://example.com/token'

        with mock.patch('time.time', lambda: now):
            for client in self.clients:
                auth = OAuth2Session(client=client, token=self.token)
                auth.send = fake_token(new_token)
                self.assertEqual(auth.fetch_token(url), new_token)


    def test_web_app_fetch_token(self):
        # Ensure the state parameter is used, see issue #105.
        client = OAuth2Session('foo', state='somestate')
        self.assertRaises(MismatchingStateError, client.fetch_token,
                          'https://i.b/token',
                          authorization_response='https://i.b/no-state?code=abc')

    def test_client_id_proxy(self):
        sess = OAuth2Session('test-id')
        self.assertEqual(sess.client_id, 'test-id')
        sess.client_id = 'different-id'
        self.assertEqual(sess.client_id, 'different-id')
        sess._client.client_id = 'something-else'
        self.assertEqual(sess.client_id, 'something-else')
        del sess.client_id
        self.assertIsNone(sess.client_id)

    def test_access_token_proxy(self):
        sess = OAuth2Session('test-id')
        self.assertIsNone(sess.access_token)
        sess.access_token = 'test-token'
        self.assertEqual(sess.access_token, 'test-token')
        sess._client.access_token = 'different-token'
        self.assertEqual(sess.access_token, 'different-token')
        del sess.access_token
        self.assertIsNone(sess.access_token)

    def test_token_proxy(self):
        token = {
            'access_token': 'test-access',
        }
        sess = OAuth2Session('test-id', token=token)
        self.assertEqual(sess.access_token, 'test-access')
        self.assertEqual(sess.token, token)
        token['access_token'] = 'something-else'
        sess.token = token
        self.assertEqual(sess.access_token, 'something-else')
        self.assertEqual(sess.token, token)
        sess._client.access_token = 'different-token'
        token['access_token'] = 'different-token'
        self.assertEqual(sess.access_token, 'different-token')
        self.assertEqual(sess.token, token)
        # can't delete token attribute
        with self.assertRaises(AttributeError):
            del sess.token

    def test_authorized_false(self):
        sess = OAuth2Session('foo')
        self.assertFalse(sess.authorized)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_authorized_true(self):
        def fake_token(token):
            def fake_send(r, **kwargs):
                resp = mock.MagicMock()
                resp.text = json.dumps(token)
                return resp
            return fake_send
        url = 'https://example.com/token'

        for client in self.clients:
            sess = OAuth2Session(client=client)
            sess.send = fake_token(self.token)
            self.assertFalse(sess.authorized)
            sess.fetch_token(url)
            self.assertTrue(sess.authorized)

