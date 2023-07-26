import base64
from datetime import datetime, timedelta

import requests

from boum.api_client import constants
from boum.api_client.v1.endpoint import Endpoint
from boum.api_client.v1.models import DeviceModel, UserModel, DeviceDataModel


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
            str = constants.API_URL_PROD, session: requests.Session = requests.Session()):
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
        self._email = None
        self.__access_token: str | None = None
        self.__refresh_token: bytes | None = None
        self.__password: bytes | None = None

        if email and password:
            self._email = email
            self._password = password
        elif refresh_token:
            self._refresh_token = refresh_token
        else:
            raise ValueError('Either email and password or refresh_token must be set')

        self._session = session
        self.root = RootEndpoint(base_url + '/v1', refresh_access_token=self._refresh_access_token)

    @property
    def _access_token(self) -> str | None:
        return self.__access_token

    @_access_token.setter
    def _access_token(self, value: str | None):
        self.__access_token = value
        self._session.headers.update({'Authorization': f'{self.__access_token}'})

    @property
    def _refresh_token(self) -> str | None:
        if self.__refresh_token:
            return base64.b64decode(self.__refresh_token).decode("utf-8")
        return None

    @_refresh_token.setter
    def _refresh_token(self, value: str | None):
        self.__refresh_token = base64.b64encode(value.encode('utf-8')) if value else None

    @property
    def _password(self) -> str | None:
        if self.__password:
            return base64.b64decode(self.__password).decode("utf-8")
        return None

    @_password.setter
    def _password(self, value: str | None):
        self.__password = base64.b64encode(value.encode('utf-8')) if value else None

    def __enter__(self) -> "ApiClient":
        """Connect to the API and sign in or refresh the access token."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from the API."""
        self.disconnect()

    def disconnect(self):
        self._session.close()
        self.root.session = None

    def connect(self):
        self.root.session = self._session
        if self._access_token:
            pass
        elif self._refresh_token:
            self._refresh_access_token()
        else:
            self._signin()

    def _signin(self):
        self._access_token, self._refresh_token = self.root.auth.signin.post(
            self._email, self._password)

    def _refresh_access_token(self):
        if not self._refresh_token:
            raise AttributeError('Refresh token not set')

        self._access_token = self.root.auth.token.post(self._refresh_token)


class AuthTokenEndpoint(Endpoint):

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "AuthTokenEndpoint":
        return super().__get__(parent, owner)

    def post(self, refresh_token: str):
        if not isinstance(refresh_token, str):
            raise ValueError('refresh_token must be a string')

        payload = {'refreshToken': refresh_token}
        response = self._post(payload)
        data = response.json()['data']
        return data['accessToken']


class AuthSigninEndpoint(Endpoint):

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "AuthSigninEndpoint":
        return super().__get__(parent, owner)

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
    def __get__(self, parent, owner: type) -> "AuthEndpoint":
        return super().__get__(parent, owner)


class DevicesDataEndpoint(Endpoint):
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "DevicesDataEndpoint":
        return super().__get__(parent, owner)

    def get(self, start: datetime = None, end: datetime = None, interval: timedelta = None):
        if self._parent.is_collection:
            raise AttributeError('Cannot get data for a collection of devices')
        if start is not None and not isinstance(start, datetime):
            raise ValueError('start must be a datetime')
        if end is not None and not isinstance(end, datetime):
            raise ValueError('end must be a datetime')
        if interval is not None and not isinstance(interval, timedelta):
            raise ValueError('interval must be a timedelta')

        query_parameters = {}
        if start:
            query_parameters['timeStart'] = start.strftime(self.DATETIME_FORMAT)
        if end:
            query_parameters['timeEnd'] = end.strftime(self.DATETIME_FORMAT)
        if interval:
            interval_seconds = int(interval.total_seconds())
            query_parameters['interval'] = f'{interval_seconds}s'

        response = self._get(query_parameters=query_parameters)
        return DeviceDataModel.from_payload(response.json()['data'])


class DevicesClaimEndpoint(Endpoint):

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "DevicesClaimedEndpoint":
        return super().__get__(parent, owner)

    def put(self):
        self._put()

    def delete(self):
        if self.is_resource:
            raise AttributeError('Cannot unclaim from a specific user')
        self._delete()

class DevicesClaimedEndpoint(Endpoint):

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "DevicesClaimEndpoint":
        return super().__get__(parent, owner)

    def get(self, include_details: bool = False) -> list[str | dict] | DeviceModel:
        response = self._get()
        data = response.json()['data']
        if self.is_collection:
            if include_details:
                return data
            return [d['id'] for d in data]

        device_model = DeviceModel.from_payload(data)
        return device_model


class DevicesEndpoint(Endpoint):
    data = DevicesDataEndpoint('data')
    claim = DevicesClaimEndpoint('claim')
    claimed = DevicesClaimedEndpoint('claimed')

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "DevicesEndpoint":
        return super().__get__(parent, owner)

    def post(self) -> str:
        if self.is_resource:
            raise ValueError('Cannot post to a specific device')
        response = self._post()
        data = response.json()['data']
        return data['deviceId']

    def get(self, include_details: bool = False) -> list[str | dict] | DeviceModel:
        response = self._get()
        data = response.json()['data']
        if self.is_collection:
            if include_details:
                return data
            return [d['id'] for d in data]

        device_model = DeviceModel.from_payload(data)
        return device_model

    def patch(self, device_model: DeviceModel):
        if self.is_collection:
            raise ValueError('Cannot patch a collection of devices')
        if not isinstance(device_model, DeviceModel):
            raise ValueError('device_model must be a DeviceModel')

        payload = device_model.to_payload()
        self._patch(payload)

    def delete(self):
        if self.is_collection:
            raise ValueError('Cannot delete a collection of devices')
        raise NotImplementedError()


class UsersEndpoint(Endpoint):

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "UsersEndpoint":
        return super().__get__(parent, owner)

    def get(self) -> UserModel:
        response = self._get()
        payload = response.json()['data']
        return UserModel.from_payload(payload)


class RootEndpoint(Endpoint):
    devices = DevicesEndpoint('devices')
    auth = AuthEndpoint('auth')
    users = UsersEndpoint('users')

    # pylint: disable=useless-parent-delegation
    def __get__(self, parent, owner: type) -> "RootEndpoint":
        return super().__get__(parent, owner)
