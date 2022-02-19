============
Contributing
============

Test simple changes
===================

Requests-OAuthlib is using `tox`_ as main test tool.
It helps creating the required virtualenv for your python version.
For example, if you have installed Python3.7:

.. sourcecode:: bash

   $ tox -e py37


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

   $ pyenv install 2.7.18
   $ pyenv install 3.4.10
   $ pyenv install 3.5.10
   $ pyenv install 3.6.14
   $ pyenv install 3.7.11
   $ pyenv install pypy2.7-7.1.1
   $ pyenv install pypy3.6-7.1.1


Publishing a release (for maintainer role)
==========================================

Maintainer tasks should always be kept to minimum. Once a release is ready, the suggested approach can be followed:

#. Create new branch release-X.Y.Z
#. Update the HISTORY.rst file
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
