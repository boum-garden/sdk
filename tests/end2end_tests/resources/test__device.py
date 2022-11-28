from datetime import datetime, timedelta, time

import pytest

from boum.api_client import constants
from boum.api_client.v1.client import ApiClient
from boum.resources.device import Device
from tests.end2end_tests.fixtures import EMAIL, PASSWORD, DEVICE_ID


@pytest.fixture(scope='module')
def client():
    return ApiClient(EMAIL, PASSWORD, constants.API_URL_LOCAL)


@pytest.fixture(scope='module')
def device(client):
    return Device(DEVICE_ID, client)


class TestGetDeviceIds:
    @pytest.mark.flaky(reruns=3)
    def test__get_device_ids__returns_list_with_device_id(self, client):
        with client:
            result = Device.get_device_ids(client)
            assert isinstance(result, list)
            assert DEVICE_ID in result


class TestPumpState:
    def test__set_pump_state__works(self, client, device):
        with client:
            device.pump_state = True

    def test__get_pump_state__works(self, client, device):
        with client:
            result = device.pump_state
            assert isinstance(result, bool)


class TestRefillTime:
    def test__set_refill_time__works(self, client, device):
        with client:
            device.refill_time = time(3, 32)

    def test__get_refill_time__works(self, client, device):
        with client:
            result = device.refill_time
            assert isinstance(result, time)


class TestDeviceData:
    def test__without_arguments__returns_data(self, client, device):
        with client:
            result = device.get_telemetry_data()
            for k, v in result.items():
                assert isinstance(k, str)
                assert isinstance(v, list)

    def test__with_time_restrictions__returns_data(self, client, device):
        with client:
            start, end = datetime.now() - timedelta(days=1), datetime.now()
            result = device.get_telemetry_data(start=start, end=end)
            for k, v in result.items():
                assert isinstance(k, str)
                assert isinstance(v, list)
