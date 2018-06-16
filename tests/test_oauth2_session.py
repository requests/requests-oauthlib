from __future__ import unicode_literals
import json
import mock
import time
from base64 import b64encode
from copy import deepcopy
from unittest import TestCase

from oauthlib.common import urlencode
from oauthlib.oauth2 import TokenExpiredError, OAuth2Error
from oauthlib.oauth2 import MismatchingStateError
from oauthlib.oauth2 import WebApplicationClient, MobileApplicationClient
from oauthlib.oauth2 import LegacyApplicationClient, BackendApplicationClient
from requests_oauthlib import OAuth2Session, TokenUpdated, TokenRequestDenied
import requests_mock


fake_time = time.time()


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

        self.requests_mock = requests_mock.mock()
        self.requests_mock.start()
        self.addCleanup(self.requests_mock.stop)

    def test_add_token(self):
        self.requests_mock.get('https://i.b', text='Ok')

        for client in self.all_clients:
            auth = OAuth2Session(client=client, token=self.token)
            resp = auth.get('https://i.b')
            self.assertEqual(200, resp.status_code)

        self.assertEqual(len(self.all_clients),
                         len(self.requests_mock.request_history))

        token = 'Bearer ' + self.token['access_token']
        for r in self.requests_mock.request_history:
            self.assertEqual(token, r.headers.get(str('Authorization'), None))

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
    def test_refresh_token_request_no_refresh(self):
        self.expired_token = dict(self.token)
        self.expired_token['expires_in'] = '-1'
        del self.expired_token['expires_at']

        # No auto refresh setup
        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.expired_token)
            self.assertRaises(TokenExpiredError, auth.get, 'https://i.b')

        self.assertFalse(self.requests_mock.called)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_refresh_token_request_refresh_no_update(self):
        self.expired_token = dict(self.token)
        self.expired_token['expires_in'] = '-1'
        del self.expired_token['expires_at']

        m1 = self.requests_mock.get('https://i.b')
        m2 = self.requests_mock.post('https://i.b/refresh', json=self.token)

        # Auto refresh but no auto update
        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.expired_token,
                    auto_refresh_url='https://i.b/refresh')
            self.assertRaises(TokenUpdated, auth.get, 'https://i.b')

        self.assertFalse(m1.called)
        self.assertEquals(len(self.clients), m2.call_count)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_refresh_token_request_refresh_and_update(self):
        self.expired_token = dict(self.token)
        self.expired_token['expires_in'] = '-1'
        del self.expired_token['expires_at']

        m1 = self.requests_mock.get('https://i.b')
        m2 = self.requests_mock.post('https://i.b/refresh', json=self.token)

        token_updater = mock.MagicMock()

        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.expired_token,
                    auto_refresh_url='https://i.b/refresh',
                    token_updater=token_updater)
            resp = auth.get('https://i.b')
            self.assertEqual(200, resp.status_code)

        self.assertEquals(len(self.clients), m1.call_count)
        self.assertEquals(len(self.clients), m2.call_count)
        self.assertEquals(len(self.clients), token_updater.call_count)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_refresh_token_request_refresh_and_update_2(self):
        self.expired_token = dict(self.token)
        self.expired_token['expires_in'] = '-1'
        del self.expired_token['expires_at']

        m1 = self.requests_mock.get('https://i.b')
        m2 = self.requests_mock.post('https://i.b/refresh', json=self.token)

        token_updater = mock.MagicMock()

        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.expired_token,
                    auto_refresh_url='https://i.b/refresh',
                    token_updater=token_updater)
            auth.get('https://i.b', client_id='foo', client_secret='bar')

        self.assertEquals(len(self.clients), m1.call_count)
        self.assertEquals(len(self.clients), m2.call_count)
        self.assertEquals(len(self.clients), token_updater.call_count)

        token = (b"Basic " + b64encode(b"foo:bar")).decode('latin1')
        for r in m2.request_history:
            self.assertEquals(token, r.headers["Authorization"])

        for c in token_updater.call_args_list:
            self.assertEqual(c, mock.call(self.token))

    @mock.patch("time.time", new=lambda: fake_time)
    def test_token_from_fragment(self):
        mobile = MobileApplicationClient(self.client_id)
        response_url = 'https://i.b/callback#' + urlencode(self.token.items())
        auth = OAuth2Session(client=mobile)
        self.assertEqual(auth.token_from_fragment(response_url), self.token)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_fetch_token_good(self):
        url = 'https://example.com/token'
        self.requests_mock.post(url, json=self.token)

        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.token)
            self.assertEqual(auth.fetch_token(url), self.token)

        self.assertEqual(len(self.clients), self.requests_mock.call_count)

    @mock.patch("time.time", new=lambda: fake_time)
    def test_fetch_token_invalid(self):
        url = 'https://example.com/token'
        self.requests_mock.post(url, json={'error': 'invalid_request'})

        for client in self.clients:
            auth = OAuth2Session(client=client, token=self.token)
            self.assertRaises(OAuth2Error, auth.fetch_token, url)

        self.assertEqual(len(self.clients), self.requests_mock.call_count)

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

        self.requests_mock.post(url, json=new_token)

        with mock.patch('time.time', lambda: now):
            for client in self.clients:
                auth = OAuth2Session(client=client, token=self.token)
                self.assertEqual(auth.fetch_token(url), new_token)

            self.assertTrue(len(self.clients), self.requests_mock.call_count)

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
        url = 'https://example.com/token'
        self.requests_mock.post(url, json=self.token)

        for client in self.clients:
            sess = OAuth2Session(client=client)
            self.assertFalse(sess.authorized)
            sess.fetch_token(url)
            self.assertTrue(sess.authorized)

        self.assertEqual(len(self.clients), self.requests_mock.call_count)

    def test_token_fetch_invalid_status_code(self):
        url = 'https://example.com/token'
        self.requests_mock.post(url,
                                json={'message': 'Failure'},
                                status_code=403)

        for client in self.clients:
            sess = OAuth2Session(client=client)
            self.assertRaises(
                TokenRequestDenied,
                sess.fetch_token,
                url
            )

        self.assertEqual(len(self.clients), self.requests_mock.call_count)
