import os
import re
import logging

class DebugModeTokenFilter(logging.Filter): # <-- inherent from the Filter class
    def __init__(self):
        super().__init__()
        # set the behavior/configuration of the filter by the environment variable 
        self.mode = os.getenv('DEBUG_MODE_TOKEN_FILTER', 'DEFAULT').upper() 

    def filter(self, record):
        if self.mode == "MASK":
            # While this doesn't directly target the headers as @erlendvollset 's post originally targets
            # this wider approach of targeting the "Bearer" key word I believe provides complete coverage.
            # However I would still recommend some more research to see if this regex would need to be improved
            # to provide a secure/trusted solution.
            record.msg = re.sub(r'Bearer (\w+)', '[MASKED]', record.getMessage())
        elif self.mode == "SUPPRESS":
            return False
        elif self.mode == "DEFAULT":
            msg = "Your logger, when in DEBUG mode, will log TOKENS"
            raise Warning(msg)
        return True