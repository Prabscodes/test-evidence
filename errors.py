class UserInputError(ValueError):
    """Explicit app-authored message safe to return; never wrap provider exceptions."""


class ProviderFailure(Exception):
    """Only app-owned categories/messages; never carry upstream bodies or secrets."""
    MESSAGES = {
        'timeout': (504, 'Model request timed out. No conclusion was accepted. The provider may still be finishing; check its status before manually starting another review. Your inputs are preserved. No automatic retry was sent.'),
        'unavailable': (503, 'Could not reach or complete a request to the model server. Check that it is running and the configured endpoint is correct. It may still be finishing an interrupted request. No conclusion was accepted and no automatic retry was sent.'),
        'model_not_loaded': (503, 'The model endpoint or model name was not found. Confirm the server is running and its loaded model name matches the app configuration. No conclusion was accepted.'),
        'input_rejected': (400, 'The model server rejected this review input. Shorten the excerpts or check its context limit and supported request settings. No conclusion was accepted.'),
        'access_denied': (502, 'The provider refused access. Check its server-side configuration; do not paste credentials into the review. No conclusion was accepted.'),
        'http_failure': (502, 'The model server could not complete this request. Check its local status and logs before manually trying again. No conclusion was accepted and no automatic retry was sent.'),
    }

    def __init__(self, code):
        self.code = code if code in self.MESSAGES else 'http_failure'
        self.http_status, self.message = self.MESSAGES[self.code]
        super().__init__(self.message)
