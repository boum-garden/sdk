import functools
from abc import ABC
from typing import Callable

import requests


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

    def __init__(
            self, base_url: str, path: str, parent: "EndpointClient | None",
            resource_id: str | None = None):
        """
        Parameters
        ----------
            base_url : str
                The url of the parent endpoint.
            path : str
                The path segment of the endpoint.
            parent : EndpointClient | None
                The parent endpoint.
            resource_id : str | None
                The id of the resource that this endpoint represents. If it is none, the enpoint
                represents a collection of resources.
        """
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

    @staticmethod
    def handle_response(func: Callable[..., requests.Response]):
        """Decorator to handle the response of the requests."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response

        return wrapper

    @handle_response
    def _get(self, query_parameters: dict = None):
        """Send a GET request to the endpoint."""
        return self._session.get(url=self.url, params=query_parameters)

    @handle_response
    def _post(self, payload: dict = None, query_parameters: dict = None):
        """Send a POST request to the endpoint."""
        return self._session.post(url=self.url, json=payload, params=query_parameters)

    @handle_response
    def _patch(self, payload: dict = None, query_parameters: dict = None):
        """Send a PATCH request to the endpoint."""
        return self._session.patch(url=self.url, json=payload, params=query_parameters)

    @handle_response
    def _delete(self, query_parameters: dict = None):
        """Send a DELETE request to the endpoint."""
        return self._session.delete(url=self.url, params=query_parameters)
