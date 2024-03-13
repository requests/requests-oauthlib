#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

from setuptools import setup


# Get the version
version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open("requests_oauthlib/__init__.py", "r") as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")


APP_NAME = "requests-oauthlib"

# Publish Helper.
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


def readall(path):
    with open(path) as fp:
        return fp.read()


setup(
    name=APP_NAME,
    version=VERSION,
    description="OAuthlib authentication support for Requests.",
    long_description=readall("README.rst") + "\n\n" + readall("HISTORY.rst"),
    long_description_content_type="text/x-rst",
    author="Kenneth Reitz",
    author_email="me@kennethreitz.com",
    url="https://github.com/requests/requests-oauthlib",
    packages=["requests_oauthlib", "requests_oauthlib.compliance_fixes"],
    python_requires=">=3.4",
    install_requires=["oauthlib>=3.0.0", "requests>=2.0.0"],
    extras_require={"rsa": ["oauthlib[signedtoken]>=3.0.0"]},
    license="ISC",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    zip_safe=False,
    tests_require=['mock;python_version<"3.3"', "requests-mock"],
    test_suite="tests",
)
