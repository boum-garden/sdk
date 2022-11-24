import requests as requests

from boum import constants
from boum.api_client_v1.endpoint import EndpointClient


class DevicesDataEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)

    def get(self):
        if not self._resource_id:
            raise ValueError('Cannot get data for a collection of devices')
        return self._get


class DevicesEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.data = DevicesDataEndpointClient(self._url, 'data')

    def post(self):
        if self._resource_id:
            raise ValueError('Cannot post to a specific device')
        return self._post()

    def get(self):
        return self._get()

    def patch(self):
        if not self._resource_id:
            raise ValueError('Cannot patch a collection of devices')
        return self._patch()

    def delete(self):
        if not self._resource_id:
            raise ValueError('Cannot delete a collection of devices')
        return self._delete()


class AuthSignupEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)

    def post(self, email: str, password: str):
        payload = {'email': email, 'password': password}
        return self._post(payload)


class AuthSigninEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)

    def post(self, email: str, password: str):
        payload = {'email': email, 'password': password}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken'], data['refreshToken']


class AuthTokenEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)

    def post(self, refresh_token: str):
        payload = {'refreshToken': refresh_token}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken']


class AuthEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.signup = AuthSignupEndpointClient(self._url, 'signup')
        self.signin = AuthSigninEndpointClient(self._url, 'signin')
        self.token = AuthTokenEndpointClient(self._url, 'token')


class RootEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.device = DevicesEndpointClient(self._url, 'device')
        self.auth = AuthEndpointClient(self._url, 'auth')


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

    def _refresh_access_token(self):
        if not self._session:
            raise AttributeError('Session not set')

        access_token = self.endpoints.auth.token.post(self._refresh_token)
        self._set_auth_header(access_token)

    def _set_auth_header(self, access_token):
        self._session.headers = {'Authorization': '{}'.format(access_token)}
