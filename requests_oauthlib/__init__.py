# ruff: noqa: F401
import logging

from .oauth1_auth import OAuth1
from .oauth1_session import OAuth1Session
from .oauth2_auth import OAuth2
from .oauth2_session import OAuth2Session, TokenUpdated

from .log_filters import DebugModeTokenFilter

__version__ = "2.0.0"

import requests

if requests.__version__ < "2.0.0":
    msg = (
        "You are using requests version %s, which is older than "
        "requests-oauthlib expects, please upgrade to 2.0.0 or later."
    )
    raise Warning(msg % requests.__version__)

logging.getLogger("requests_oauthlib").addHandler(logging.NullHandler())
logging.getLogger("requests_oauthlib").addFilter(DebugModeTokenFilter())

for filter_ in logging.getLogger("requests_oauthlib").filters:
    if isinstance(filter_, DebugModeTokenFilter):
        if filter_.mode == 'DEFAULT':
            msg = "Your logger, when in DEBUG mode, will log TOKENS"
            logging.warning(msg)
        break 
