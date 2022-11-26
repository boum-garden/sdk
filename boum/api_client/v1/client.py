from boum.api_client import constants
from boum.api_client.v1.endpoints import RootEndpointClient


class ApiClient:
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
        >>> with ApiClient("email", "password") as client:
        >>>
        >>> # Get call to the devices collection
        >>> device_ids = client.root.devices.get()
        >>>
        >>> # Get call to a specific device
        >>> device_states = client.root.devices(device_ids[0]).get()
        >>>
        >>> # Patch call to a specific device
        >>> client.root.devices(device_ids[0]).patch(DeviceState())
        >>>
        >>> # Get call to a devices data
        >>> data = client.root.devices(device_ids[0]).data.get()
    """

    def __init__(
            self, email: str, password: str, host_url: str = constants.API_URL_PROD, ):
        """
        Parameters
        ----------
            email: str
                The email of the user.
            password: str
                The password of the user.
            host_url: str
                The URL of the API. Defaults to the production API.
        """

        self.root = RootEndpointClient(host_url, 'v1')
        self._email = email
        self._password = password
        self._refresh_token = ''

    def __enter__(self) -> "ApiClient":
        """Connect to the API and sign in."""
        self.root.connect()
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
