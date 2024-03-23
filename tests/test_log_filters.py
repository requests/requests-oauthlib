import unittest
from unittest.mock import patch
from logging import LogRecord
from requests_oauthlib.log_filters import DebugModeTokenFilter

class TestDebugModeTokenFilter(unittest.TestCase):

    def setUp(self):
        self.record = LogRecord(name="test", level=20, pathname=None, lineno=None, msg="Bearer i-am-a-token", args=None, exc_info=None)

    @patch.dict('os.environ', {'DEBUG_MODE_TOKEN_FILTER': 'MASK'})
    def test_mask_mode(self):
        filter = DebugModeTokenFilter()
        filter.filter(self.record)
        self.assertIn('[MASKED]', self.record.msg)

    @patch.dict('os.environ', {'DEBUG_MODE_TOKEN_FILTER': 'SUPPRESS'})
    def test_suppress_mode(self):
        filter = DebugModeTokenFilter()
        result = filter.filter(self.record)
        self.assertFalse(result) # Check that nothing is logged

    @patch.dict('os.environ', {'DEBUG_MODE_TOKEN_FILTER': 'DEFAULT'})
    def test_default_mode(self):
        filter = DebugModeTokenFilter()
        with self.assertRaises(Warning) as context:
            filter.filter(self.record)
        self.assertTrue("Your logger, when in DEBUG mode, will log TOKENS" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
