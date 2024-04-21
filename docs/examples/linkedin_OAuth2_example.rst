LinkedIn OAuth 2.0 Tutorial
===========================

Overview
--------
This tutorial guides you through the process of setting up OAuth 2.0 authentication with LinkedIn. You will learn how to register your application with LinkedIn, obtain necessary credentials, and implement the OAuth 2.0 flow to authenticate users and access LinkedIn's API.

Prerequisites
-------------
Before you begin, you need to have a LinkedIn developer account. Register your application with LinkedIn to obtain the ``client_id`` and ``client_secret`` needed for the OAuth process. You will also be able to learn about application scope which while it is not unqiue/sensitive information, will need to be set to successfully make a call to a protected resource/endpoint.

Register Your Application
-------------------------
1. Visit the LinkedIn Developer portal.
2. Create and register an application with Linkedin, the resource and indentity provider.
3. Note down the ``client_id`` and ``client_secret`` provided after registration.

Setting Up the OAuth Flow
-------------------------
This is a simple script demonstrating the workflow using this library in a cli environment.

1. Ensure you have installed the ``requests_oauthlib`` package. If not, you can install it using pip:
   
   .. code-block:: bash

       pip install requests_oauthlib

2. Update the cooresponding variable values with your ``client_id`` and ``client_secret`` obtained from LinkedIn.

3. Update then run the script. Follow the instructions printed in the console.

Python Script
-------------
Plug your ``client_id`` and a ``client_secret`` into the command line interactive example below.

.. literalinclude:: linkedin_OAuth2_example.py
   :language: python
