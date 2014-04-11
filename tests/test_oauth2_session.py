from __future__ import unicode_literals
import json
import mock
import time
import unittest

from oauthlib.common import urlencode
from oauthlib.oauth2 import TokenExpiredError, InvalidRequestError
from oauthlib.oauth2 import MismatchingStateError
from oauthlib.oauth2 import WebApplicationClient, MobileApplicationClient
from oauthlib.oauth2 import LegacyApplicationClient, BackendApplicationClient
from requests_oauthlib import OAuth2Session, TokenUpdated


fake_time = time.time()


class OAuth2SessionTest(unittest.TestCase):

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
        def fake_token(token):
            def fake_send(r, **kwargs):
                resp = mock.MagicMock()
                resp.text = json.dumps(token)
                return resp
            return fake_send
        url = 'https://example.com/token'

        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.token)
            auth.send = fake_token(self.token)
            self.assertEqual(auth.fetch_token(url), self.token)

        error = {'error': 'invalid_request'}
        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.token)
            auth.send = fake_token(error)
            self.assertRaises(InvalidRequestError, auth.fetch_token, url)


    def test_web_app_fetch_token(self):
        # Ensure the state parameter is used, see issue #105.
        client = OAuth2Session('foo', state='somestate')
        self.assertRaises(MismatchingStateError, client.fetch_token,
                          'https://i.b/token',
                          authorization_response='https://i.b/no-state?code=abc')
