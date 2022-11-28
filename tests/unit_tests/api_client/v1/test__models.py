from datetime import time

from boum.api_client.v1.models import DeviceState


class TestDeviceState:

    def test__create_from_payload__works(self):
        payload_1 = {
            'maxPumpDuration': '10min', 'pumpState': 'off', 'refillTime': '01:53',
            'refillInterval': '3days'
        }
        payload_2 = {
            'maxPumpDuration': '11min', 'pumpState': 'on', 'refillTime': '00:00',
            'refillInterval': '4days'
        }

        device_state_1 = DeviceState.from_payload(payload_1)
        device_state_2 = DeviceState.from_payload(payload_2)

        assert not device_state_1.pump_state
        assert device_state_1.max_pump_duration == '10min'
        assert device_state_1.refill_time == time(1, 53)
        assert device_state_1.refill_interval == 3

        assert device_state_2.pump_state
        assert device_state_2.max_pump_duration == '11min'
        assert device_state_2.refill_time == time(0, 0)
        assert device_state_2.refill_interval == 4

    def test__to_payload_complete__works(self):
        device_state_1 = DeviceState(
            max_pump_duration='10min', pump_state=False,
            refill_time=time(1, 53), refill_interval=3)
        device_state_2 = DeviceState(
            max_pump_duration='11min', pump_state=True,
            refill_time=time(0, 0), refill_interval=4)

        assert device_state_1.to_payload() == {
            'maxPumpDuration': '10min', 'pumpState': 'off', 'refillTime': '01:53',
            'refillInterval': '3days'
        }
        assert device_state_2.to_payload() == {
            'maxPumpDuration': '11min', 'pumpState': 'on', 'refillTime': '00:00',
            'refillInterval': '4days'

        }

    def test__to_payload_partial__works(self):
        device_state_1 = DeviceState(max_pump_duration='10min', pump_state=False)
        device_state_2 = DeviceState(refill_time=time(0, 0))

        assert device_state_1.to_payload() == {'maxPumpDuration': '10min', 'pumpState': 'off'}
        assert device_state_2.to_payload() == {'refillTime': '00:00'}
