"""
This model tests the validation of the model classes on isntantiation, the cnoversion into
payload objects and the conversion from payload objects into model objects.
"""

from datetime import time

import pytest
from boum.api_client.v1.models import DeviceStateModel, DeviceModel, DeviceDataModel
from tests.fixtures.api import DevicesWithIdDataGet


class TestDeviceModel:

    def test__from_payload_complete__works(self):
        payload = {
            'reported': {
                'maxPumpDuration': '10min', 'pumpState': 'off', 'refillTime': '01:53',
                'refillInterval': '3days'
            },
            'desired': {
                'maxPumpDuration': '11min', 'pumpState': 'on', 'refillTime': '00:00',
                'refillInterval': '4days'
            }
        }

        result = DeviceModel.from_payload(payload)

        assert result.reported_state.pump_state is False
        assert result.reported_state.max_pump_duration_minutes == 10
        assert result.reported_state.refill_interval_days == 3
        assert result.reported_state.refill_time == time(1, 53)

        assert result.desired_state.pump_state
        assert result.desired_state.max_pump_duration_minutes == 11
        assert result.desired_state.refill_time == time(0, 0)
        assert result.desired_state.refill_interval_days == 4

    def test__from_payload_empty__works(self):
        payload = {'desired': {}, 'reported': {}}

        result = DeviceModel.from_payload(payload)

        assert result.reported_state.pump_state is None
        assert result.reported_state.max_pump_duration_minutes is None
        assert result.reported_state.refill_interval_days is None
        assert result.reported_state.refill_time is None

        assert result.desired_state.pump_state is None
        assert result.desired_state.max_pump_duration_minutes is None
        assert result.desired_state.refill_time is None
        assert result.desired_state.refill_interval_days is None

    def test__from_payload_none__works(self):
        payload = {}

        result = DeviceModel.from_payload(payload)

        assert result.reported_state is None
        assert result.desired_state is None

    def test__to_payload_complete__works(self):
        device_model = DeviceModel(
            DeviceStateModel(
                max_pump_duration_minutes=10, pump_state=False,
                refill_time=time(1, 53), refill_interval_days=3)
        )

        result = device_model.to_payload()

        assert result == {
            'state': {
                'desired': {
                    'maxPumpDuration': '10min', 'pumpState': 'off', 'refillTime': '01:53',
                    'refillInterval': '3days'
                }
            }
        }

    def test__to_payload_empty__works(self):
        device_model = DeviceModel(reported_state=DeviceStateModel())

        result = device_model.to_payload()

        assert result == {'state': {'reported': {}}}


class TestDeviceStateModel:

    @pytest.mark.parametrize('value', [-1, 0, 24 * 60, '10', time(0, 0)])
    def test__max_pump_duration_minutes_invalid__raises_value_error(self, value):
        with pytest.raises(ValueError):
            DeviceStateModel(max_pump_duration_minutes=value)

    def test__max_pump_duration_minutes_none__works(self):
        result = DeviceStateModel(max_pump_duration_minutes=None)
        assert result.max_pump_duration_minutes is None

    @pytest.mark.parametrize('value', [-1, '10', time(0, 0)])
    def test__refill_interval_days_invalid__raises_value_error(self, value):
        with pytest.raises(ValueError):
            DeviceStateModel(refill_interval_days=value)

    def test__refill_interval_days_none__works(self):
        result = DeviceStateModel(refill_interval_days=None)
        assert result.refill_interval_days is None

    @pytest.mark.parametrize('value', [-1, 1, '10', '10:33'])
    def test__refill_time_invalid__raises_value_error(self, value):
        with pytest.raises(ValueError):
            DeviceStateModel(refill_time=value)

    def test__refill_time_none__works(self):
        result = DeviceStateModel(refill_time=None)
        assert result.refill_time is None

    @pytest.mark.parametrize('value', [-1, 1, '10', time(0, 0)])
    def test__pump_state_invalid__raises_value_error(self, value):
        with pytest.raises(ValueError):
            DeviceStateModel(pump_state=value)

    def test__pump_state_none__works(self):
        result = DeviceStateModel(pump_state=None)
        assert result.pump_state is None

class TestDeviceDataModel:
    def test__from_payload__works(self):
        result = DeviceDataModel.from_payload(DevicesWithIdDataGet.data)
        expected = DeviceDataModel(DevicesWithIdDataGet.data_clean)
        assert result == expected
