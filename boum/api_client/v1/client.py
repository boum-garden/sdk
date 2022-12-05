from datetime import datetime

from boum.api_client import constants
from boum.api_client.v1.endpoint import Endpoint
from boum.api_client.v1.models import DeviceModel, UserModel


class ApiClient:
    # noinspection PyUnresolvedReferences
    """
        Client for the boum API v1.

        It is implemented as a context manager, so you can use it with
        the `with` statement. It will automatically connect and disconnect to the API. It will also
        automatically refresh the access token when it expires.

        A detailed documentation of the endpoint hierarchy can be found at the swagger page of
        the API (base_url/swagger).

        Attributes
        ----------
            root: EndpointClient
                The root endpoint client. It contains all the other nested endpoint clients.

        Example
        -------
            >>> from boum.api_client.v1.client import ApiClient
            >>> from boum.api_client.v1.models import DeviceModel
            >>>
            >>> client = ApiClient(email, password, base_url=base_url)
            >>> # or ApiClient(refresh_token='token', base_url=base_url)
            >>>
            >>> with client:
            ...     # Get call to the devices collection
            ...     device_ids = client.root.devices.get()
            ...     # Get call to a specific device
            ...     device_states = client.root.devices(device_id).get()
            ...     # Patch call to a specific device
            ...     client.root.devices(device_id).patch(DeviceModel())
            ...     # Get call to a devices data
            ...     data = client.root.devices(device_id).data.get()
        """

    def __init__(
            self, email: str = None, password: str = None, refresh_token: str = None, base_url:
            str = constants.API_URL_PROD, ):
        """
        Parameters
        ----------
            email
                The email of the user. Required if `refresh_token` is not set.
            password
                The password of the user. Required if `refresh_token` is not set.
            refresh_token
                The refresh token of the user. Required if `email` and `password` are not set.
            base_url
                The URL of the API. Defaults to the production API.
        """

        if not (email and password) and not refresh_token:
            raise ValueError('Either email and password or refresh_token must be set')
        ApiClient._instance = self
        self.root = RootEndpoint(base_url + '/v1', refresh_access_token=self._refresh_access_token)
        self._email = email
        self._password = password
        self._refresh_token = refresh_token

    def __enter__(self) -> "ApiClient":
        """Connect to the API and sign in or refresh the access token."""
        self.root.connect()
        if self._refresh_token:
            self._refresh_access_token()
        else:
            self._signin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from the API."""
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

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "AuthTokenEndpoint":
        return super().__get__(instance, owner)

    def post(self, refresh_token: str):
        if not isinstance(refresh_token, str):
            raise ValueError('refresh_token must be a string')

        payload = {'refreshToken': refresh_token}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken']


class AuthSigninEndpoint(Endpoint):

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "AuthSigninEndpoint":
        return super().__get__(instance, owner)

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

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "AuthEndpoint":
        return super().__get__(instance, owner)


class DevicesDataEndpoint(Endpoint):
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "DevicesDataEndpoint":
        return super().__get__(instance, owner)

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

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "DevicesClaimEndpoint":
        return super().__get__(instance, owner)

    def put(self):
        self._put()

    def delete(self):
        if self.resource_id:
            raise AttributeError('Cannot unclaim from a specific user')
        self._delete()


class DevicesEndpoint(Endpoint):
    data = DevicesDataEndpoint('data')
    claim = DevicesClaimEndpoint('claim')

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "DevicesEndpoint":
        return super().__get__(instance, owner)

    def post(self) -> str:
        if self.resource_id:
            raise ValueError('Cannot post to a specific device')
        response = self._post()
        data = response.json()['data']
        return data['deviceId']

    def get(self) -> list[str] | DeviceModel:
        response = self._get()
        data = response.json()['data']
        if not self.resource_id:
            return [d['id'] for d in data]

        device_model = DeviceModel.from_payload(data)
        return device_model

    def patch(self, device_model: DeviceModel):
        if not self.resource_id:
            raise ValueError('Cannot patch a collection of devices')
        if not isinstance(device_model, DeviceModel):
            raise ValueError('device_model must be a DeviceModel')

        payload = device_model.to_payload()
        self._patch(payload)

    def delete(self):
        if not self.resource_id:
            raise ValueError('Cannot delete a collection of devices')
        raise NotImplementedError()


class UsersEndpoint(Endpoint):

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "UsersEndpoint":
        return super().__get__(instance, owner)

    def get(self) -> UserModel:
        response = self._get()
        payload = response.json()['data']
        return UserModel.from_payload(payload)


class RootEndpoint(Endpoint):
    devices = DevicesEndpoint('devices')
    auth = AuthEndpoint('auth')
    users = UsersEndpoint('users')

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "RootEndpoint":
        return super().__get__(instance, owner)
