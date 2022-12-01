from datetime import time

from boum.api_client.v1.models import DeviceStateModel, DeviceModel


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
        assert result.reported_state.max_pump_duration == 10
        assert result.reported_state.refill_interval == 3
        assert result.reported_state.refill_time == time(1, 53)

        assert result.desired_state.pump_state
        assert result.desired_state.max_pump_duration == 11
        assert result.desired_state.refill_time == time(0, 0)
        assert result.desired_state.refill_interval == 4

    def test__from_payload_empty__works(self):
        payload = {'desired': {}, 'reported': {}}

        result = DeviceModel.from_payload(payload)

        assert result.reported_state.pump_state is None
        assert result.reported_state.max_pump_duration is None
        assert result.reported_state.refill_interval is None
        assert result.reported_state.refill_time is None

        assert result.desired_state.pump_state is None
        assert result.desired_state.max_pump_duration is None
        assert result.desired_state.refill_time is None
        assert result.desired_state.refill_interval is None

    def test__from_payload_none__works(self):
        payload = {}

        result = DeviceModel.from_payload(payload)

        assert result.reported_state is None
        assert result.desired_state is None

    def test__to_payload_complete__works(self):
        device_model = DeviceModel(
            DeviceStateModel(
                max_pump_duration=10, pump_state=False,
                refill_time=time(1, 53), refill_interval=3)
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
