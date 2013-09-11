Web App Example of OAuth 2 web application flow
==================================================

OAuth is commonly used by web applications and not command line applications
like the other tutorials show case. The example below shows what such
a web application might look like using an imaginary web framework and
GitHub as a provider. It should be easily transferrable to any
web framework.

If you are using Flask there is a `working example gist`_.

.. _`working example gist`: https://gist.github.com/ib-lundgren/6507798

.. code-block:: py

   from requests_oauthlib import OAuth2Session
    
    
   # This information is obtained upon registration of a new GitHub
   client_id = "<your client key>"
   client_secret = "<your client secret>"
   authorization_base_url = 'https://github.com/login/oauth/authorize'
   token_url = 'https://github.com/login/oauth/access_token'
    
    
   @app.route("/")

   class PreAuthorization(RequestHandler):

       route = '/'

       def get(request):
           """Step 1: User Authorization.
        
           Redirect the user/resource owner to the OAuth provider (i.e. Github)
           using an URL with a few key OAuth parameters.
           """
           github = OAuth2Session(client_id)
           authorization_url, state = github.authorization_url(authorization_base_url)
        
           # State is used to prevent CSRF, keep this for later.
           request.session['oauth_state'] = state
           return self.redirect(authorization_url)
    
    
   # Step 2: User authorization, this happens on the provider.
    

   class PostAuthorization(RequestHandler):

       route = '/callback'

       def get(request):
           """ Step 3: Retrieving an access token.
        
           The user has been redirected back from the provider to your registered
           callback URL. With this redirection comes an authorization code included
           in the redirect URL. We will use that to obtain an access token.
           """
        
           github = OAuth2Session(client_id, state=request.session['oauth_state'])
           token = github.fetch_token(token_url, client_secret=client_secret,
                                      authorization_response=request.url)
        
           # At this point you can fetch protected resources but lets save
           # the token and show how this is done from a persisted token
           # in /profile.
           request.session['oauth_token'] = token
        
           return self.redirect(url_for('.profile'))
    
    
   class UsingTheOAuthToken(RequestHandler):

       route = '/profile'

       def get(request):
           """Fetching a protected resource using an OAuth 2 token.
           """
           github = OAuth2Session(client_id, token=request.session['oauth_token'])
           profile_data = github.get('https://api.github.com/user').json()
           return self.jsonify(profile_data)
