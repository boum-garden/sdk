import functools
import logging
from abc import ABC
from datetime import datetime
from typing import Callable

import requests

from boum.api_client.v1.models import DeviceState


class EndpointClient(ABC):
    """Baseclass for all endpoint clients.

    With this class you can create a tree hierarchy of endpoints that model the topology of a
    REST API.

    The subclasses of this class should implement the methods that correspond to the http verbs that
    the endpoint supports, using the provided private methods.

    if there are nested endpoints, the subclasses should also have properties that represent the
    nested paths. These properties should also be subclasses of EndpointClient.

    Attributes
    ----------
        url : str
            The full url of the endpoint.
        resource_id : str | None
            The id of the resource that this endpoint represents. If it is none, the enpoint
            represents a collection of resources.
    """

    _session: requests.Session | None = None
    _headers: dict[str, str] = {}
    _refresh_access_token: Callable[[], None] = None
    _access_token_issue_prefix = 'Access token'

    def __init__(
            self, base_url: str, path: str, parent:
            "EndpointClient | None", resource_id: str | None = None,
            refresh_access_token: Callable[[], None] = None):
        """
        Parameters
        ----------
            base_url
                The url of the parent endpoint.
            path
                The path segment of the endpoint.
            parent
                The parent endpoint.
            resource_id
                The id of the resource that this endpoint represents. If it is none, the enpoint
                represents a collection of resources.
            refresh_access_token
                A callable that refreshes the access token.
        """
        EndpointClient._refresh_access_token = refresh_access_token
        self._base_url = base_url
        self._path = path
        self.resource_id = resource_id
        self.url = '/'.join(s.strip('/') for s in [base_url, path, resource_id] if s)
        self._parent = parent

    def __call__(self, resource_id: str):
        return type(self)(self._base_url, self._path, self._parent, resource_id)

    @classmethod
    def connect(cls):
        """Connect all endpoints to the API."""
        EndpointClient._session = requests.Session()
        EndpointClient._session.headers = cls._headers

    @classmethod
    def disconnect(cls):
        """Disconnect all endpoints from the API."""
        EndpointClient._session.close()
        EndpointClient._session = None

    @classmethod
    def is_connected(cls):
        """Check if the endpoints are connected to the API."""
        return cls._session is not None

    @classmethod
    def set_access_token(cls, access_token: str):
        """Set the access token for the endpoints."""
        auth_header = {'Authorization': f'{access_token}'}
        EndpointClient._headers.update(auth_header)

    # noinspection PyMethodParameters
    # pylint: disable=no-self-argument no-member protected-access
    def _request_handler(func: Callable[..., requests.Response]):
        """Decorator to apply the response handling method to the request methods"""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            logging.info("Calling %s on %s...", func.__name__, self.url)
            response = func(self, *args, **kwargs)

            if response.status_code == 401 \
                    and str.startswith(response.json()['message'], self._access_token_issue_prefix):
                logging.info('Access token expired. Refreshing...')
                self._refresh_access_token()
                logging.info('Access token refreshed. Retrying request...')
                response = func(self, *args, **kwargs)
            else:
                response.raise_for_status()

            logging.info('Request successful.')
            return response

        return wrapper

    # noinspection PyArgumentList
    @_request_handler
    def _get(self, query_parameters: dict = None):
        """Send a GET request to the endpoint."""
        return self._session.get(url=self.url, params=query_parameters)

    # noinspection PyArgumentList
    @_request_handler
    def _post(self, payload: dict = None, query_parameters: dict = None):
        """Send a POST request to the endpoint."""
        return self._session.post(url=self.url, json=payload, params=query_parameters)

    # noinspection PyArgumentList
    @_request_handler
    def _patch(self, payload: dict = None, query_parameters: dict = None):
        """Send a PATCH request to the endpoint."""
        return self._session.patch(url=self.url, json=payload, params=query_parameters)

    # noinspection PyArgumentList
    @_request_handler
    def _delete(self, query_parameters: dict = None):
        """Send a DELETE request to the endpoint."""
        return self._session.delete(url=self.url, params=query_parameters)


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
            self, base_url: str, path: str, refresh_access_token: Callable[[], None]):
        super().__init__(base_url, path, None, None, refresh_access_token)
        self.devices = DevicesEndpointClient(self.url, 'devices', self)
        self.auth = AuthEndpointClient(self.url, 'auth', self)
