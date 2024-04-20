======================
Documentation examples
======================

Examples found in documentation must be tested to be sure we have the appropriate
coverage and be sure new releases are tested against regressions.

Also, it helps testing any changes in public Identity Providers.

Currently few tests are covered, and ``selenium`` package is used to interact with browser. Feel free to have a look at the base class in ``tests/examples/base.py`` to reuse utility specially crafted for testing samples in documentation.

Identity Providers available for tests
======================================

Currently only an Auth0 test provider is available but new can be created on request. Following are the environment variables :

- Auth0 https://auth0.com/ :

  - ``AUTH0_USERNAME``
  - ``AUTH0_PASSWORD``
  - ``AUTH0_DOMAIN``
  - ``AUTH0_PKCE_CLIENT_ID``

Guidelines to write samples
===========================

Documentation
^^^^^^^^^^^^^

In order to write a testable sample, like an easy copy/paste, it is recommended to separate the python code from the documentation as below :

.. code-block::

   .. literalinclude:: xyz_foobar.py
     :language: python

Verify if formatting is correct by checking :

.. code-block:: bash

  tox -e docs
  # output located in docs/_build/html/index.html
                
                
Python example
^^^^^^^^^^^^^^

It's recommended to write a python example with either predefined placeholder variables for environment setup properties (like identity provider tenants identifiers/secrets), and use ``input()`` when user interaction is required. Feel free to reuse an existing example like ``docs/examples/native_spa_pkce_auth0.py`` and its associated test.

Python tests
^^^^^^^^^^^^

You can write new tests in ``tests/examples/test_*py`` and inherit of base classes found in ``tests/examples/base.py`` based on your needs.

Don't forget to skip python tests if you require an environment variables, also don't store any secrets or leak tenant informations in git.

Skip tests example as below:

.. code-block:: python

        self.client_id = os.environ.get("AUTH0_PKCE_CLIENT_ID")
        self.idp_domain = os.environ.get("AUTH0_DOMAIN")

        if not self.client_id or not self.idp_domain:
            self.skipTest("native auth0 is not configured properly")


Then the sample can be copy paste into a python console 

Environment variables
^^^^^^^^^^^^^^^^^^^^^

Once referencing environment variables, you have to set them in the Github Actions. Any maintainers can do it, and it's the role of the maintainer to create a test tenant with test clients.

Example on how to set new env secrets with `GitHub CLI <https://cli.github.com/>`_:

.. code-block:: bash

    gh secret set AUTH0_PASSWORD --body "secret"


Helper Interfaces
=================

.. autoclass:: tests.examples.Sample
    :members:

.. autoclass:: tests.examples.Browser
    :members:
