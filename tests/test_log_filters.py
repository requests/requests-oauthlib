import unittest
from unittest.mock import patch
import logging
from requests_oauthlib.log_filters import DebugModeTokenFilter

class TestDebugModeTokenFilter(unittest.TestCase):

    def setUp(self):
        self.record = logging.LogRecord(name="test", level=logging.DEBUG, pathname=None, lineno=None, msg="Bearer i-am-a-little-token-here-is-my-scope-and-here-is-my-hash", args=None, exc_info=None)

    @patch.dict('os.environ', {'REQUESTS_OAUTHLIB_DEBUG_MODE_TOKEN_FILTER': 'MASK'})
    def test_mask_mode(self):
        filter = DebugModeTokenFilter()
        filter.filter(self.record)
        self.assertIn('[MASKED]', self.record.msg)

    @patch.dict('os.environ', {'REQUESTS_OAUTHLIB_DEBUG_MODE_TOKEN_FILTER': 'SUPPRESS'})
    def test_suppress_mode(self):
        filter = DebugModeTokenFilter()
        filter.filter(self.record)
        self.assertEqual(" ", self.record.msg) # No logging

    # @patch.dict('os.environ', {'REQUESTS_OAUTHLIB_DEBUG_MODE_TOKEN_FILTER': 'DEFAULT'})
    # def test_default_mode_raises_warning(self):
    #     with self.assertLogs('requests_oauthlib', level='WARN') as cm:
    #         DebugModeTokenFilter()
    #         logging.getLogger("requests_oauthlib").addFilter(DebugModeTokenFilter())
    #         # Trigger the log event to check for the warning message
    #         logging.getLogger("requests_oauthlib").debug(self.record.getMessage())

    #     self.assertIn("Your logger, when in DEBUG mode, will log TOKENS", cm.output[0])


if __name__ == '__main__':
    unittest.main()
