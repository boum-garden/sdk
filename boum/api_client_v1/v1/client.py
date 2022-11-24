import requests as requests

from boum.api_client_v1.endpoint import EndpointClient


class ApiClient:
    def __init__(self, host_url: str):
        self.endpoints = RootEndpointClient(host_url, '')
        self._session: None | requests.Session = None

    def __enter__(self) -> "ApiClient":
        self._session = requests.Session()
        self.endpoints._session = self._session
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
        self._session = None

    def signin(self, email: str, password: str):
        if not self._session:
            raise AttributeError('Session not set')

        self.endpoints.auth.signin.post(email, password)


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
        return self._post(payload)


class AuthTokenEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)

    def post(self, refresh_token: str):
        payload = {'refreshToken': refresh_token}
        return self._post(payload)


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
