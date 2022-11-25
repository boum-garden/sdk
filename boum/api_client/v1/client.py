import requests as requests

from boum import constants
from boum.api_client.v1.endpoints import RootEndpointClient


class ApiClient:
    def __init__(self, host_url: str = constants.API_URL_PROD):
        self.endpoints = RootEndpointClient(host_url, '')
        self._session: None | requests.Session = None
        self._access_token = ''
        self._refresh_token = ''

    def __enter__(self) -> "ApiClient":
        self._session = requests.Session()
        self.endpoints.session = self._session
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
        self._session = None

    def signin(self, email: str, password: str):
        if not self._session:
            raise AttributeError('Session not set')
        access_token, self._refresh_token = self.endpoints.auth.signin.post(email, password)
        self._set_auth_header(access_token)

    def refresh_access_token(self):
        if not self._session:
            raise AttributeError('Session not set')
        if not self._refresh_token:
            raise AttributeError('Refresh token not set')

        access_token = self.endpoints.auth.token.post(self._refresh_token)
        self._set_auth_header(access_token)

    def _set_auth_header(self, access_token: str):
        self._session.headers = {'Authorization': f'{access_token}'}
