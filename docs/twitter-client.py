# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import requests
import webbrowser
from urlparse import parse_qs
from requests_oauthlib import OAuth1

# Current release of requests_oauthlib (0.2.0) does not automatically encode the parameters in the call to OAuth1 to utf-8.
# Encodes explicitly all the strings that go into the OAuth1 constructor to utf-8 to circumvent the error 'ValueError: Only unicode objects are escapable.'

# Client(consumer) key and secret. Obtained by registering the app at dev.twitter.com
consumer_key = u'<your-apps-consumer-key>'
consumer_secret = u'<your-apps-consumer-secret>'

# Twitter OAuth endpoints
request_token_url = u"https://api.twitter.com/oauth/request_token"
authorize_url = u"https://api.twitter.com/oauth/authorize?oauth_token="
access_token_url = u"https://api.twitter.com/oauth/access_token"

# Obtain the request tokens. These are used to redirect the user to the authorization URL to get the verifier PIN
oauth = OAuth1(consumer_key, client_secret=consumer_secret)
r = requests.post(url=request_token_url, auth=oauth)

# Parse the content to get the request token and secret
credentials = parse_qs(r.content)
request_token = credentials['oauth_token'][0]
request_token = unicode(request_token, 'utf-8')
request_secret = credentials['oauth_token_secret'][0]
request_secret = unicode(request_secret, 'utf-8')

# Prompt the user to verify the app at the authorization URL and get the verifier PIN
authorize_url = authorize_url + request_token
print "Redirecting you to the browser to authorize...", authorize_url
webbrowser.open(authorize_url)
verifier = raw_input('Please enter your PIN : ')
verifier = unicode(verifier, 'utf-8')

# We use the verifier provided by the user to get the access tokens
oauth = OAuth1(consumer_key, client_secret=consumer_secret, resource_owner_key=request_token, resource_owner_secret=request_secret, verifier=verifier)
r = requests.post(url=access_token_url, auth=oauth)

# Parse the access token and secret from the content.
credentials = parse_qs(r.content)
access_token = credentials.get('oauth_token')[0]
access_token = unicode(access_token, 'utf-8')
access_secret = credentials.get('oauth_token_secret')[0]
access_secret = unicode(access_secret, 'utf-8')

oauth = OAuth1(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=access_secret)
r = requests.get(url=u"https://api.twitter.com/1/account/settings.json", auth=oauth)

print r.content