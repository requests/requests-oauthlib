from __future__ import unicode_literals
import os


def is_secure_transport(uri):
    """Check if the uri is over ssl."""
    if os.environ.get('DEBUG'):
        return True
    return uri.lower().startswith('https://')
