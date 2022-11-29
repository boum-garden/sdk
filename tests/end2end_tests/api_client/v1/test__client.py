from datetime import datetime, timedelta

import pytest
from requests import HTTPError

from boum.api_client import constants
from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models.device_state import DeviceState
from tests.end2end_tests.fixtures import EMAIL, PASSWORD, DEVICE_ID


@pytest.fixture
def client():
    return ApiClient(EMAIL, PASSWORD, base_url=constants.API_URL_LOCAL)


class TestApiClient:

    def test__instantiate_with_refresh_token__works(self, client):
        with client:
            _, refresh_token = client.root.auth.signin.post(EMAIL, PASSWORD)

        with ApiClient(refresh_token=refresh_token, base_url=constants.API_URL_LOCAL):
            pass


class TestAuthEndpoints:

    def test__signin_endpoint(self, client):
        with client:
            access_token, refresh_token = client.root.auth.signin.post(EMAIL, PASSWORD)

        assert access_token
        assert refresh_token

    def test__refresh_token_endpoint(self, client):
        with client:
            access_token_1, refresh_token = client.root.auth.signin.post(EMAIL, PASSWORD)
            access_token_2 = client.root.auth.token.post(refresh_token)

        assert access_token_2
        assert access_token_1 != access_token_2


class TestDevicesEndpointPost:

    def test__without_device_id__raises_http_error_401(self, client):
        with client, pytest.raises(HTTPError):
            client.root.devices.post()

    def test__with_device_id__raises_value_error(self, client):
        with client, pytest.raises(ValueError):
            client.root.devices(DEVICE_ID).post()


class TestDevicesEndpointsGet:

    @pytest.mark.flaky(reruns=3)
    def test__without_device_id__returns_list_with_device_id(self, client):
        with client:
            result = client.root.devices.get()
            assert result == [DEVICE_ID]

    def test__with_device_id__returns_device_states(self, client):
        with client:
            desired, reported = client.root.devices(DEVICE_ID).get()
            assert isinstance(desired, DeviceState)
            assert isinstance(reported, DeviceState)


class TestDevicesEndpointsPatch:

    def test__without_device_id__raises_value_error(self, client):
        desired_device_state = DeviceState()
        with client, pytest.raises(ValueError):
            client.root.devices.patch(desired_device_state)

    def test__with_device_id__works(self, client):
        desired_device_state = DeviceState()
        with client:
            client.root.devices(DEVICE_ID).patch(desired_device_state)


class TestDevicesDataEndpointGet:

    def test__without_arguments__returns_data(self, client):
        with client:
            data = client.root.devices(DEVICE_ID).data.get()
            for k, v in data.items():
                assert isinstance(k, str)
                assert isinstance(v, list)

    def test__with_time_restrictions__returns_data(self, client):
        with client:
            start, end = datetime.now() - timedelta(days=1), datetime.now()
            data = client.root.devices(DEVICE_ID).data.get(start=start, end=end)
            for k, v in data.items():
                assert isinstance(k, str)
                assert isinstance(v, list)


class TestDevicesClaimEndpointPut:

    def test__without_user_id__claims_to_currently_digned_in_user(self, client):
        with client:
            client.root.devices.claim.put()

    def test__with_device_id__works(self, client):
        with client:
            client.root.devices(DEVICE_ID).claim.put()


