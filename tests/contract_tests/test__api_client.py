import pytest
from requests import HTTPError

from boum import constants
from boum.api_client_v1.v1.client import ApiClient
from boum.api_client_v1.v1.models import DeviceState

EMAIL = 'ludwig.auer@gmail.com'
PASSWORD = 'Test1234'
LUDWIGS_DEVICE_ID = '8b89148b-484a-4a4f-949b-5b79f4f6637f'


@pytest.fixture
def client():
    return ApiClient(constants.API_URL_LOCAL)


class TestAuthEndpoints:

    def test__signin_endpoint(self, client):
        with client:
            access_token, refresh_token = client.endpoints.auth.signin.post(EMAIL, PASSWORD)

        assert access_token
        assert refresh_token

    def test__refresh_token_endpoint(self, client):
        with client:
            access_token_1, refresh_token = client.endpoints.auth.signin.post(EMAIL, PASSWORD)
            access_token_2 = client.endpoints.auth.token.post(refresh_token)

        assert access_token_2
        assert access_token_1 != access_token_2


class TestApiClient:

    def test__auth_flow__works(self, client):
        with client:
            client.signin(EMAIL, PASSWORD)
            client.refresh_access_token()

    def test__signin_with_bad_credentials__raises_http_error(self, client):
        with client:
            with pytest.raises(HTTPError):
                client.signin(EMAIL, 'bad_password')

    def test__refresh_access_token_without_token__raises_attribute_error(self, client):
        with client:
            with pytest.raises(AttributeError):
                client.refresh_access_token()


class TestDevicesEndpointPost:
    def test__post_with_device_id__raises_value_error(self, client):
        with client:
            client.signin(EMAIL, PASSWORD)
            with pytest.raises(ValueError):
                client.endpoints.devices('some_device_id').post()

    def test__post_without_device_id__returns_device_id(self, client):
        with client:
            client.signin(EMAIL, PASSWORD)
            device_id = client.endpoints.devices.post()
            assert device_id
            assert isinstance(device_id, str)


class TestDevicesEndpointsGet:

    def test__get_without_device_id__returns_collection_of_ids(self, client):
        with client:
            client.signin(EMAIL, PASSWORD)
            device_ids = client.endpoints.devices.get()

        assert len(device_ids) > 0

    def test__get_with_device_id__returns_device_states(self, client):
        with client:
            client.signin(EMAIL, PASSWORD)
            device_id = client.endpoints.devices.get()[0]
            desired, reported = client.endpoints.devices(device_id).get()
            assert isinstance(desired, DeviceState)
            assert isinstance(reported, DeviceState)


class TestDevicesEndpointsPatch:

    def test__patch_without_device_id__raises_value_error(self, client):
        desired_device_state = DeviceState()
        with client:
            client.signin(EMAIL, PASSWORD)
            with pytest.raises(ValueError):
                client.endpoints.devices.patch(desired_device_state)

    def test__patch_with_device_id__works(self, client):
        desired_device_state = DeviceState()
        with client:
            client.signin(EMAIL, PASSWORD)
            device_id = client.endpoints.devices.get()[0]
            client.endpoints.devices(device_id).patch(desired_device_state)


class TestDevicesDataEndpoint

    def