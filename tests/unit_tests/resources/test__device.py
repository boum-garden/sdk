"""
This module tests the Device resource abstraction up to the calls to the API with the session
object. It relies on the API fixtures and on their correct representation of the actual API.
"""

from unittest.mock import Mock

import pytest

from boum.api_client.v1.client import ApiClient
from boum.resources.device import Device
from tests.fixtures.api import AuthSigningPost, DevicesGet, DEVICE_ID, PASSWORD, EMAIL, BASE_URL, \
    DevicesWithIdGet, DevicesWithIdPatch, DevicesWithIdClaimPut, USER_ID, \
    DevicesWithIdClaimWithIdPut, DevicesWithIdClaimDelete, DevicesWithIdDataGet


@pytest.fixture
def session_mock():
    return Mock()


@pytest.fixture
def client(session_mock):
    session_mock.post.return_value = AuthSigningPost.response
    with ApiClient(EMAIL, PASSWORD, base_url=BASE_URL, session=session_mock) as client:
        session_mock.post = Mock()
        yield client


@pytest.fixture
def device(client):
    return Device(DEVICE_ID, client)


class TestGetDeviceIds:
    def test__get_device_ids__returns_list_with_device_id(self, client, session_mock):
        session_mock.get.return_value = DevicesGet.response
        result = Device.get_device_ids(client)
        assert session_mock.get.call_args == DevicesGet.call
        assert isinstance(result, list)
        assert DEVICE_ID in result


class TestSetDeviceState:
    def test__works(self, device, session_mock):
        session_mock.patch.return_value = DevicesWithIdPatch.response
        device.set_desired_device_state(DevicesWithIdPatch.desired_state)
        assert session_mock.patch.call_args == DevicesWithIdPatch.call


class TestGetDeviceState:
    def test__works(self, device, session_mock):
        session_mock.get.return_value = DevicesWithIdGet.response
        reported_result, desired_result = device.get_device_states()
        assert session_mock.get.call_args == DevicesWithIdGet.call
        assert reported_result == DevicesWithIdGet.reported_state
        assert desired_result == DevicesWithIdPatch.desired_state


class TestClaimDevice:
    def test_without_user_id__works(self, device, session_mock):
        session_mock.put.return_value = DevicesWithIdClaimPut.response
        device.claim()
        assert session_mock.put.call_args == DevicesWithIdClaimPut.call

    def test_with_user_id__works(self, device, session_mock):
        session_mock.put.return_value = DevicesWithIdClaimWithIdPut.response
        device.claim(USER_ID)
        assert session_mock.put.call_args == DevicesWithIdClaimWithIdPut.call


class TestUnClaimDevice:
    def test_without_user_id__works(self, device, session_mock):
        session_mock.delete.return_value = DevicesWithIdClaimDelete.response
        device.unclaim()
        assert session_mock.delete.call_args == DevicesWithIdClaimDelete.call


class TestGetTelemetryData:

    def test__without_arguments__returns_data(self, device, session_mock):
        session_mock.get.return_value = DevicesWithIdDataGet.response
        result = device.get_telemetry_data()
        assert session_mock.get.call_args == DevicesWithIdDataGet.call_no_args
        assert result == DevicesWithIdDataGet.data_clean

    def test__time_limit_arguments__returns_data(self, device, session_mock):
        session_mock.get.return_value = DevicesWithIdDataGet.response
        result = device.get_telemetry_data(
            start=DevicesWithIdDataGet.start, end=DevicesWithIdDataGet.end)
        assert result == DevicesWithIdDataGet.data_clean
        assert session_mock.get.call_args == DevicesWithIdDataGet.call_time_limit_args
        assert result == DevicesWithIdDataGet.data_clean
