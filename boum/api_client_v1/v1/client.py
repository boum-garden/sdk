import requests as requests

from boum import constants
from boum.api_client_v1.endpoint import EndpointClient
from boum.api_client_v1.v1.models import DeviceState


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
        self.signin = AuthSigninEndpointClient(self._url, 'signin')
        self.token = AuthTokenEndpointClient(self._url, 'token')


class DevicesDataEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)

    def get(self):
        if not self._resource_id:
            raise ValueError('Cannot get data for a collection of devices')
        response = self._get()
        data = response.json()['data']
        return [d['id'] for d in data]


class DevicesEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.data = DevicesDataEndpointClient(self._url, 'data')

    def post(self):
        if self._resource_id:
            raise ValueError('Cannot post to a specific device')
        response = self._post()
        data = response.json()['data']
        return data['deviceId']

    def get(self):
        response = self._get()
        data = response.json()['data']
        if not self._resource_id:
            return [d['id'] for d in data]

        desired_device_state = DeviceState(
            refill_time=data['desired']['refillTime'],
            max_pump_duration=data['desired']['maxPumpDuration'],
            pump_state=data['desired']['pumpState']
        )
        reported_device_state = DeviceState(
            refill_time=data['reported']['refillTime'],
            max_pump_duration=data['reported']['maxPumpDuration'],
            pump_state=data['reported']['pumpState']
        )
        return desired_device_state, reported_device_state


    def patch(self, desired_device_state: DeviceState):
        if not self._resource_id:
            raise ValueError('Cannot patch a collection of devices')

        payload = {}
        if desired_device_state.max_pump_duration is not None:
            payload['maxPumpDuration'] = desired_device_state.max_pump_duration
        if desired_device_state.refill_time is not None:
            payload['refillTime'] = desired_device_state.refill_time
        if desired_device_state.pump_state is not None:
            payload['pumpState'] = desired_device_state.pump_state

        self._patch(payload)

    def delete(self):
        if not self._resource_id:
            raise ValueError('Cannot delete a collection of devices')
        raise NotImplementedError()


class AuthSigninEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)

    def post(self, email: str, password: str):
        payload = {'email': email, 'password': password}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken'], data['refreshToken']


class RootEndpointClient(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.devices = DevicesEndpointClient(self._url, 'devices')
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

    def refresh_access_token(self):
        if not self._session:
            raise AttributeError('Session not set')
        if not self._refresh_token:
            raise AttributeError('Refresh token not set')

        access_token = self.endpoints.auth.token.post(self._refresh_token)
        self._set_auth_header(access_token)

    def _set_auth_header(self, access_token: str):
        self._session.headers = {'Authorization': f'{access_token}'}
