============
Contributing
============

Test simple changes
===================

Requests-OAuthlib is using `tox`_ as main test tool.
It helps creating the required virtualenv for your python version.
For example, if you have installed Python3.8:

.. sourcecode:: bash

   $ tox -e py38


Validate documentation changes
==============================

Tox contains also a build method to generate documentation locally.

.. sourcecode:: bash

   $ tox -e docs,readme

Then open the HTML page in `_build/html/index.html`
   

Verify all pythons versions
===========================

Requests-OAuthlib supports multiple versions of Python.
You can test all Python versions conveniently using `tox`_.

.. sourcecode:: bash

   $ tox

In order to run successfully, you will need all versions of Python installed. We recommend using `pyenv`_ to install those Python versions.

.. sourcecode:: bash

   $ pyenv install 3.8.18
   $ pyenv install pypy3.10-7.3.13
   $ pyenv global pypy3.10-7.3.13  # switch to pypy


Build and test via pipeline
===========================

If you don't want to install multiple python versions, or if you have
made changes in the pipeline code, it is possible to execute the Github Action
locally with the `act` tools available here: https://nektosact.com/usage/index.html

Run tests for `pypy3.9`:

```shell
act -W .github/workflows/run-tests.yml -j tests --matrix python-version:pypy3.9
```

Publishing a release (for maintainer role)
==========================================

Maintainer tasks should always be kept to minimum. Once a release is ready, the suggested approach can be followed:

#. Create new branch release-X.Y.Z
#. Update HISTORY.rst and AUTHORS.rst if required
#. Update the `request_oauthlib/__init__.py`
#. Raise a pull request to give a chance for all contributors to comment before publishing
#. Create a TAG vX.Y.Z. By doing this, the pipeline will automatically trigger `twine` and will publish the release to PyPi.

Once verified, complete by doing the following:

#. Create a GitHub release vX.Y.Z in the Releases tab.
#. Activate the vX.Y.Z version in the documentation (`ReadTheDocs`_)
#. Merge the PR into master branch.

That's all.

.. _`tox`: https://tox.readthedocs.io/en/latest/install.html
.. _`virtualenv`: https://virtualenv.pypa.io/en/latest/installation/
.. _`pyenv`: https://github.com/pyenv/pyenv
.. _`ReadTheDocs`: https://readthedocs.org/projects/requests-oauthlib/versions/
