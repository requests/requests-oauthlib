import unittest
from unittest.mock import patch
import logging
from requests_oauthlib.log_filters import DebugModeTokenFilter

class TestDebugModeTokenFilter(unittest.TestCase):

    def setUp(self):
        self.record = logging.LogRecord(name="test", level=logging.DEBUG, pathname=None, lineno=None, msg="Bearer i-am-a-little-token-here-is-my-scope-and-here-is-my-signature", args=None, exc_info=None)

    @patch.dict('os.environ', {'DEBUG_MODE_TOKEN_FILTER': 'MASK'})
    def test_mask_mode(self):
        filter = DebugModeTokenFilter()
        filter.filter(self.record)
        self.assertIn('[MASKED]', self.record.msg)

    @patch.dict('os.environ', {'DEBUG_MODE_TOKEN_FILTER': 'SUPPRESS'})
    def test_suppress_mode(self):
        filter = DebugModeTokenFilter()
        result = filter.filter(self.record)
        self.assertFalse(result) # No logging

    @patch.dict('os.environ', {'DEBUG_MODE_TOKEN_FILTER': 'DEFAULT'})
    def test_default_mode_raises_warning(self):
        filter = DebugModeTokenFilter()
        with self.assertRaises(Warning) as context:
            filter.filter(self.record)
        self.assertTrue("Your logger, when in DEBUG mode, will log TOKENS" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
