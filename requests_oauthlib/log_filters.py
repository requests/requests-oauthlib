import os
import re
import logging


class DebugModeTokenFilter(logging.Filter):
    """
    A logging filter that while in DEBUG mode can filter TOKENS dependent on configuration.

    This filter uses an environment variable to determine its mode, 
    which can either mask sensitive tokens in log messages, suppress logging, 
    or default to standard logging behavior with a warning.

    Attributes:
        mode (str): The mode of operation based on the environment variable
                    'DEBUG_MODE_TOKEN_FILTER'. Can be 'MASK', 'SUPPRESS', or 'DEFAULT'.
    """

    def __init__(self):
        """
        Initializes the DebugModeTokenFilter with the 'DEBUG_MODE_TOKEN_FILTER'
        environment variable.
        """
        super().__init__()
        self.mode = os.getenv(
            'REQUESTS_OAUTHLIB_DEBUG_MODE_TOKEN_FILTER', 'DEFAULT').upper()

    def filter(self, record):
        """
        Filters logs of TOKENS dependent on the configured mode.

        Args:
            record (logging.LogRecord): The log record to filter.

        Returns:
            bool: True if the record should be logged, False otherwise.
        """
        if record.levelno == logging.DEBUG:
            if self.mode == "MASK":
                record.msg = re.sub(
                    r'Bearer\s+([A-Za-z0-9\-._~+\/]+)', '[MASKED]', record.getMessage())
            elif self.mode == "SUPPRESS":
                record.msg = " "
            else:
                return False
            return True  # if mode is not MASKED then DEFAULT is implied
