#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Get the version
version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('requests_oauthlib/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")


APP_NAME = 'requests-oauthlib'

settings = dict()


# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


settings.update(
    name=APP_NAME,
    version=VERSION,
    description='OAuthlib authentication support for Requests.',
    long_description=open('README.rst').read(),
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    url='https://github.com/requests/requests-oauthlib',
    packages=find_packages(),
    install_requires=['oauthlib>=0.4.2', 'requests>=1.0.0'],
    license='ISC',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    zip_safe=False,
    tests_require=['mock'],
    test_suite='tests'
)

setup(**settings)
