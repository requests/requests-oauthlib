import os
import unittest
from . import Sample

class TestLinkedInExample(Sample, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client_id = os.environ.get("LINKEDIN_CLIENT_ID")
        self.client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        # Skip the test if the credentials are not setup
        if not self.client_id or not self.client_secret:
            self.skipTest("LinkedIn credentials are not configured properly")

    def test_linkedin_oauth_flow(self):
        self.run_sample(
            "linkedin_OAuth2_example.py", {
                'LINKEDIN_CLIENT_ID': self.client_id,
                'LINKEDIN_CLIENT_SECRET': self.client_secret,
            }
        )
        
        # Wait for the script to output the authorization URL
        authorize_url = self.wait_for_pattern("Please go here and authorize:")
        print(f"Authorization URL provided: {authorize_url}")

        mock_redirect_response = 'http://127.0.0.1/?code=A_VALID_CODE_FROM_LINKEDIN'
        # So if I am testing this examples application flow I mock everything from here on out???
        # Probably need integration/e2e testing to detect if the third part API contract is changed, breaking the example.
        self.write(mock_redirect_response)
        
        # TODO: mock the token exchange
        # TODO: mock the response from the protected endpoint api call
        # TODO: add assertions 
if __name__ == '__main__':
    unittest.main()
