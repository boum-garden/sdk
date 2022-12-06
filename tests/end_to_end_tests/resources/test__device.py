import random
from datetime import datetime, timedelta, time

import pytest

from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceStateModel
from boum.resources.device import Device
from tests.end_to_end_tests.fixtures import EMAIL, PASSWORD, DEVICE_ID, BASE_URL


@pytest.fixture(scope='module')
def client():
    with ApiClient(EMAIL, PASSWORD, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope='module')
def device(client):
    return Device(DEVICE_ID, client)


class TestGetDeviceIds:
    @pytest.mark.flaky(reruns=3)
    def test__get_device_ids__returns_list_with_device_id(self, client):
        result = Device.get_device_ids(client)
        assert isinstance(result, list)
        assert DEVICE_ID in result


class TestDeviceState:
    def test__get_and_set_pump_state__works(self, device):
        desired_state_in = DeviceStateModel(
            pump_state=random.choice([True, False]),
            refill_time=time(random.randint(0, 23), random.randint(0, 59)),
            refill_interval_days=random.randint(0, 10),
            max_pump_duration_minutes=random.randint(0, 10),
        )
        device.set_desired_device_state(desired_state_in)
        reported_state_out, desired_state_out = device.get_device_states()
        assert desired_state_in == desired_state_out
        assert isinstance(reported_state_out, DeviceStateModel)


class TestDeviceData:
    def test__without_arguments__returns_data(self, device):
        result = device.get_telemetry_data()
        for k, v in result.items():
            assert isinstance(k, str)
            assert isinstance(v, list)

    def test__with_time_restrictions__returns_data(self, device):
        start, end = datetime.now() - timedelta(days=1), datetime.now()
        result = device.get_telemetry_data(start=start, end=end)
        for k, v in result.items():
            assert isinstance(k, str)
            assert isinstance(v, list)
