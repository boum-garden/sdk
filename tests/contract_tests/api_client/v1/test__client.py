import doctest
from datetime import datetime, timedelta

import pytest

import boum.api_client.v1.client
from boum.api_client import constants
from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceState
from tests.contract_tests.fixtures import EMAIL, PASSWORD


def test__docstrings():
    execution_context = {
        'email': EMAIL,
        'password': PASSWORD,
    }
    doctest.testmod(
        boum.api_client.v1.client, raise_on_error=True, verbose=True, globs=execution_context)


@pytest.fixture
def client():
    return ApiClient(EMAIL, PASSWORD, constants.API_URL_LOCAL)


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

    def test__with_device_id__raises_value_error(self, client):
        with client:
            with pytest.raises(ValueError):
                client.root.devices('some_device_id').post()

    def test__without_device_id__returns_device_id(self, client):
        with client:
            device_id = client.root.devices.post()
            assert device_id
            assert isinstance(device_id, str)


class TestDevicesEndpointsGet:

    @pytest.mark.flaky(reruns=3)
    def test__without_device_id__returns_collection_of_ids(self, client):
        with client:
            device_ids = client.root.devices.get()

        assert len(device_ids) > 0

    def test__with_device_id__returns_device_states(self, client):
        with client:
            device_id = client.root.devices.get()[0]
            desired, reported = client.root.devices(device_id).get()
            assert isinstance(desired, DeviceState)
            assert isinstance(reported, DeviceState)


class TestDevicesEndpointsPatch:

    def test__without_device_id__raises_value_error(self, client):
        desired_device_state = DeviceState()
        with client:
            with pytest.raises(ValueError):
                client.root.devices.patch(desired_device_state)

    def test__with_device_id__works(self, client):
        desired_device_state = DeviceState()
        with client:
            device_id = client.root.devices.get()[0]
            client.root.devices(device_id).patch(desired_device_state)


class TestDevicesDataEndpointGet:

    def test__without_device_id__raises_value_error(self, client):
        with client:
            with pytest.raises(ValueError):
                client.root.devices.data.get()

    def test__with_device_id__returns_data(self, client):
        with client:
            device_id = client.root.devices.get()[0]
            data = client.root.devices(device_id).data.get()
            for k, v in data.items():
                assert isinstance(k, str)
                assert isinstance(v, list)

    def test__with_time_restrictions__returns_data(self, client):
        with client:
            device_id = client.root.devices.get()[0]
            start, end = datetime.now() - timedelta(days=1), datetime.now()
            data = client.root.devices(device_id).data.get(start=start, end=end)
            for k, v in data.items():
                assert isinstance(k, str)
                assert isinstance(v, list)