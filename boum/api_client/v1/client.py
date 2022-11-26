from boum.api_client.v1 import constants
from boum.api_client.v1.endpoints import RootEndpointClient


class ApiClient:
    def __init__(
            self, email: str, password: str, host_url: str = constants.API_URL_PROD, ):
        self.endpoints = RootEndpointClient(host_url, '')
        self._email = email
        self._password = password
        self._refresh_token = ''

    def __enter__(self) -> "ApiClient":
        self.endpoints.connect()
        self._signin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.endpoints.disconnect()

    def _signin(self):
        access_token, self._refresh_token = self.endpoints.auth.signin.post(
            self._email, self._password)
        self.endpoints.set_access_token(access_token)

    def _refresh_access_token(self):
        if not self._refresh_token:
            raise AttributeError('Refresh token not set')

        access_token = self.endpoints.auth.token.post(self._refresh_token)
        self.endpoints.set_access_token(access_token)
