from datetime import datetime

from boum.api_client import constants
from boum.api_client.v1.endpoint import Endpoint
from boum.api_client.v1.models.device_state import DeviceState


class ApiClient:
    # noinspection PyUnresolvedReferences
    """
        Client for the boum API v1.

        It is implemented as a context manager, so you can use it with
        the `with` statement. It will automatically connect and disconnect to the API. It will also
        automatically refresh the access token when it expires.

        Attributes
        ----------
            root: EndpointClient
                The root endpoint client. It contains all the other nested endpoint clients.

        Example
        -------
            >>> from boum.api_client import constants
            >>> from boum.api_client.v1.models.device_state import DeviceState
            >>> from boum.api_client.v1.client import ApiClient, RootEndpoint
            >>>
            >>> with ApiClient(email, password, base_url=base_url) as client:
            ...     # Get call to the devices collection
            ...     device_ids = client.root.devices.get()
            ...     # Get call to a specific device
            ...     device_states = client.root.devices(device_ids[0]).get()
            ...     # Patch call to a specific device
            ...     client.root.devices(device_ids[0]).patch(DeviceState())
            ...     # Get call to a devices data
            ...     data = client.root.devices(device_ids[0]).data.get()
        """

    def __init__(
            self, email: str = None, password: str = None, refresh_token: str = None, base_url:
            str = constants.API_URL_PROD, ):
        """
        Parameters
        ----------
            email: str
                The email of the user.
            password: str
                The password of the user.
            base_url: str
                The URL of the API. Defaults to the production API.
        """

        if not (email and password) and not refresh_token:
            raise ValueError('Either email and password or refresh_token must be set')
        ApiClient._instance = self
        self.root = RootEndpoint(base_url, 'v1', self._refresh_access_token)
        self._email = email
        self._password = password
        self._refresh_token = refresh_token

    def __enter__(self) -> "ApiClient":
        """Connect to the API and sign in."""
        self.root.connect()
        if self._refresh_token:
            self._refresh_access_token()
        else:
            self._signin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.root.disconnect()

    def _signin(self):
        access_token, self._refresh_token = self.root.auth.signin.post(
            self._email, self._password)
        self.root.set_access_token(access_token)

    def _refresh_access_token(self):
        if not self._refresh_token:
            raise AttributeError('Refresh token not set')

        access_token = self.root.auth.token.post(self._refresh_token)
        self.root.set_access_token(access_token)


class AuthTokenEndpoint(Endpoint):

    def post(self, refresh_token: str):
        if not isinstance(refresh_token, str):
            raise ValueError('refresh_token must be a string')

        payload = {'refreshToken': refresh_token}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken']


class AuthSigninEndpoint(Endpoint):

    def post(self, email: str, password: str):
        if not isinstance(email, str):
            raise ValueError('email must be a string')
        if not isinstance(password, str):
            raise ValueError('password must be a string')

        payload = {'email': email, 'password': password}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken'], data['refreshToken']


class AuthEndpoint(Endpoint):
    signin = AuthSigninEndpoint('signin')
    token = AuthTokenEndpoint('token')


class DevicesDataEndpoint(Endpoint):
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def get(self, start: datetime = None, end: datetime = None):
        if not self._parent.resource_id:
            raise AttributeError('Cannot get data for a collection of devices')
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


class DevicesClaimEndpoint(Endpoint):
    def put(self):
        self._put()

    def delete(self):
        if self.resource_id:
            raise AttributeError('Cannot unclaim from a specific user')
        self._delete()


class DevicesEndpoint(Endpoint):
    data = DevicesDataEndpoint('data')
    claim = DevicesClaimEndpoint('claim')

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
        return reported_device_state, desired_device_state

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


class RootEndpoint(Endpoint):
    devices = DevicesEndpoint('devices')
    auth = AuthEndpoint('auth')
