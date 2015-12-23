from __future__ import unicode_literals
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

import requests
import requests_mock
import time
try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
from requests_oauthlib.compliance_fixes import mailchimp_compliance_fix
from requests_oauthlib.compliance_fixes import weibo_compliance_fix
from requests_oauthlib.compliance_fixes import slack_compliance_fix


class FacebookComplianceFixTest(TestCase):

    def setUp(self):
        mocker = requests_mock.Mocker()
        mocker.post(
            "https://graph.facebook.com/oauth/access_token",
            text="access_token=urlencoded",
            headers={"Content-Type": "text/plain"},
        )
        mocker.start()
        self.addCleanup(mocker.stop)

        facebook = OAuth2Session('foo', redirect_uri='https://i.b')
        self.session = facebook_compliance_fix(facebook)

    def test_fetch_access_token(self):
        token = self.session.fetch_token(
            'https://graph.facebook.com/oauth/access_token',
             client_secret='bar',
             authorization_response='https://i.b/?code=hello',
        )
        self.assertEqual(token, {'access_token': 'urlencoded', 'token_type': 'Bearer'})


class LinkedInComplianceFixTest(TestCase):

    def setUp(self):
        mocker = requests_mock.Mocker()
        mocker.post(
            "https://www.linkedin.com/uas/oauth2/accessToken",
            json={"access_token": "linkedin"},
        )
        mocker.post(
            "https://api.linkedin.com/v1/people/~/shares",
            status_code=201,
            json={
              "updateKey": "UPDATE-3346389-595113200",
              "updateUrl": "https://www.linkedin.com/updates?discuss=abc&scope=xyz"
            }
        )
        mocker.start()
        self.addCleanup(mocker.stop)

        linkedin = OAuth2Session('foo', redirect_uri='https://i.b')
        self.session = linkedin_compliance_fix(linkedin)

    def test_fetch_access_token(self):
        token = self.session.fetch_token(
            'https://www.linkedin.com/uas/oauth2/accessToken',
            client_secret='bar',
            authorization_response='https://i.b/?code=hello',
        )
        self.assertEqual(token, {'access_token': 'linkedin', 'token_type': 'Bearer'})

    def test_protected_request(self):
        self.session.token = {"access_token": 'dummy-access-token'}
        response = self.session.post(
            "https://api.linkedin.com/v1/people/~/shares"
        )
        url = response.request.url
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["oauth2_access_token"], ["dummy-access-token"])


class MailChimpComplianceFixTest(TestCase):

    def setUp(self):
        mocker = requests_mock.Mocker()
        mocker.post(
            "https://login.mailchimp.com/oauth2/token",
            json={"access_token": "mailchimp", "expires_in": 0, "scope": None},
        )
        mocker.start()
        self.addCleanup(mocker.stop)

        mailchimp = OAuth2Session('foo', redirect_uri='https://i.b')
        self.session = mailchimp_compliance_fix(mailchimp)

    def test_fetch_access_token(self):
        token = self.session.fetch_token(
            "https://login.mailchimp.com/oauth2/token",
            client_secret='bar',
            authorization_response='https://i.b/?code=hello',
        )
        # Times should be close
        approx_expires_at = time.time() + 3600
        actual_expires_at = token.pop('expires_at')
        self.assertAlmostEqual(actual_expires_at, approx_expires_at, places=2)

        # Other token values exact
        self.assertEqual(token, {'access_token': 'mailchimp', 'expires_in': 3600})

        # And no scope at all
        self.assertNotIn('scope', token)


class WeiboComplianceFixTest(TestCase):

    def setUp(self):
        mocker = requests_mock.Mocker()
        mocker.post(
            "https://api.weibo.com/oauth2/access_token",
            json={"access_token": "weibo"},
        )
        mocker.start()
        self.addCleanup(mocker.stop)

        weibo = OAuth2Session('foo', redirect_uri='https://i.b')
        self.session = weibo_compliance_fix(weibo)

    def test_fetch_access_token(self):
        token = self.session.fetch_token(
            'https://api.weibo.com/oauth2/access_token',
            client_secret='bar',
            authorization_response='https://i.b/?code=hello',
        )
        self.assertEqual(token, {'access_token': 'weibo', 'token_type': 'Bearer'})


class SlackComplianceFixTest(TestCase):

    def setUp(self):
        mocker = requests_mock.Mocker()
        mocker.post(
            "https://slack.com/api/oauth.access",
            json={
              "access_token": "xoxt-23984754863-2348975623103",
              "scope": "read",
            },
        )
        for method in ("GET", "POST"):
            mocker.request(
                method=method,
                url="https://slack.com/api/auth.test",
                json={
                  "ok": True,
                  "url": "https://myteam.slack.com/",
                  "team": "My Team",
                  "user": "cal",
                  "team_id": "T12345",
                  "user_id": "U12345",
                }
            )
        mocker.start()
        self.addCleanup(mocker.stop)

        slack = OAuth2Session('foo', redirect_uri='https://i.b')
        self.session = slack_compliance_fix(slack)

    def test_protected_request(self):
        self.session.token = {"access_token": 'dummy-access-token'}
        response = self.session.get(
            "https://slack.com/api/auth.test"
        )
        url = response.request.url
        query = parse_qs(urlparse(url).query)
        self.assertNotIn("token", query)
        body = response.request.body
        data = parse_qs(body)
        self.assertEqual(data["token"], ["dummy-access-token"])

    def test_protected_request_override_token_get(self):
        self.session.token = {"access_token": 'dummy-access-token'}
        response = self.session.get(
            "https://slack.com/api/auth.test",
            data={"token": "different-token"},
        )
        url = response.request.url
        query = parse_qs(urlparse(url).query)
        self.assertNotIn("token", query)
        body = response.request.body
        data = parse_qs(body)
        self.assertEqual(data["token"], ["different-token"])

    def test_protected_request_override_token_post(self):
        self.session.token = {"access_token": 'dummy-access-token'}
        response = self.session.post(
            "https://slack.com/api/auth.test",
            data={"token": "different-token"},
        )
        url = response.request.url
        query = parse_qs(urlparse(url).query)
        self.assertNotIn("token", query)
        body = response.request.body
        data = parse_qs(body)
        self.assertEqual(data["token"], ["different-token"])

    def test_protected_request_override_token_url(self):
        self.session.token = {"access_token": 'dummy-access-token'}
        response = self.session.get(
            "https://slack.com/api/auth.test?token=different-token",
        )
        url = response.request.url
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["token"], ["different-token"])
        self.assertIsNone(response.request.body)
