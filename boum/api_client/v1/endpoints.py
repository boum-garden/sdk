from datetime import datetime

from boum.api_client.endpoint import EndpointClient
from boum.api_client.v1.models import DeviceState


class AuthTokenEndpointClient(EndpointClient):

    def post(self, refresh_token: str):
        if not isinstance(refresh_token, str):
            raise ValueError('refresh_token must be a string')

        payload = {'refreshToken': refresh_token}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken']


class AuthEndpointClient(EndpointClient):
    def __init__(
            self, base_url: str, path: str, parent: EndpointClient):
        super().__init__(base_url, path, parent)
        self.signin = AuthSigninEndpointClient(self.url, 'signin', self)
        self.token = AuthTokenEndpointClient(self.url, 'token', self)


class DevicesDataEndpointClient(EndpointClient):
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def get(self, start: datetime = None, end: datetime = None):
        if not self._parent.resource_id:
            raise ValueError('Cannot get data for a collection of devices')
        if start is not None and not isinstance(start, datetime):
            raise ValueError('start must be a datetime')
        if end is not None and not isinstance(end, datetime):
            raise ValueError('end must be a datetime')

        query_parameters = {}
        if start:
            query_parameters['timeStart'] = start.strftime(self.DATETIME_FORMAT)
        if end:
            query_parameters['timeEnd'] = end.strftime(self.DATETIME_FORMAT)

        response = self._get(query_parameters=query_parameters)
        return response.json()['data']['timeSeries']


class DevicesEndpointClient(EndpointClient):
    def __init__(
            self, base_url: str, path: str, parent: EndpointClient, resource_id: str | None = None):
        super().__init__(base_url, path, parent, resource_id)
        self.data = DevicesDataEndpointClient(self.url, 'data', self)

    def post(self):
        if self.resource_id:
            raise ValueError('Cannot post to a specific device')
        response = self._post()
        data = response.json()['data']
        return data['deviceId']

    def get(self):
        response = self._get()
        data = response.json()['data']
        if not self.resource_id:
            return [d['id'] for d in data]

        desired_device_state = DeviceState.from_payload(data['desired'])
        reported_device_state = DeviceState.from_payload(data['reported'])
        return desired_device_state, reported_device_state

    def patch(self, desired_device_state: DeviceState):
        if not self.resource_id:
            raise ValueError('Cannot patch a collection of devices')
        if not isinstance(desired_device_state, DeviceState):
            raise ValueError('desired_device_state must be a DeviceState')

        payload = desired_device_state.to_payload()

        self._patch(payload)

    def delete(self):
        if not self.resource_id:
            raise ValueError('Cannot delete a collection of devices')
        raise NotImplementedError()


class AuthSigninEndpointClient(EndpointClient):

    def post(self, email: str, password: str):
        if not isinstance(email, str):
            raise ValueError('email must be a string')
        if not isinstance(password, str):
            raise ValueError('password must be a string')

        payload = {'email': email, 'password': password}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken'], data['refreshToken']


class RootEndpointClient(EndpointClient):
    def __init__(
            self, base_url: str, path: str):
        super().__init__(base_url, path, None)
        self.devices = DevicesEndpointClient(self.url, 'devices', self)
        self.auth = AuthEndpointClient(self.url, 'auth', self)
