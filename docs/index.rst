.. Requests-OAuthlib documentation master file, created by
   sphinx-quickstart on Fri May 10 11:49:01 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Requests-OAuthlib: OAuth for Humans
===================================

Requests-OAuthlib uses the Python
`Requests <https://github.com/kennethreitz/requests/>`_ and
`OAuthlib <https://github.com/idan/oauthlib/>`_ libraries to provide an
easy-to-use Python interface for building OAuth1 and OAuth2 clients.


Overview
--------

A simple Flask application which connects to the Github OAuth2 API looks
approximately like this:

.. code-block:: python

    from requests_oauthlib import OAuth2Session

    from flask import Flask, request, redirect, session, url_for
    from flask.json import jsonify

    # This information is obtained upon registration of a new GitHub
    client_id = "<your client key>"
    client_secret = "<your client secret>"
    authorization_base_url = 'https://github.com/login/oauth/authorize'
    token_url = 'https://github.com/login/oauth/access_token'

    @app.route("/login")
    def login():
        github = OAuth2Session(client_id)
        authorization_url, state = github.authorization_url(authorization_base_url)

        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        return redirect(authorization_url)

    @app.route("/callback")
    def callback(): 
        github = OAuth2Session(client_id, state=session['oauth_state'])
        token = github.fetch_token(token_url, client_secret=client_secret,
                                   authorization_response=request.url)

        return jsonify(github.get('https://api.github.com/user').json())


The above is a truncated example. A full working example is available here:
:ref:`real_example`


Getting Started:
================

.. toctree::
   :maxdepth: 2

   oauth1_workflow
   oauth2_workflow
   examples/examples

   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

