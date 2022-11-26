from boum.api_client.endpoint import EndpointClient
from boum.api_client.v1.models import DeviceState


class AuthTokenEndpointClient(EndpointClient):

    def post(self, refresh_token: str):
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

    def get(self):
        if not self._parent.resource_id:
            raise ValueError('Cannot get data for a collection of devices')
        response = self._get()
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
        if not self.resource_id:
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
        if not self.resource_id:
            raise ValueError('Cannot delete a collection of devices')
        raise NotImplementedError()


class AuthSigninEndpointClient(EndpointClient):

    def post(self, email: str, password: str):
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
