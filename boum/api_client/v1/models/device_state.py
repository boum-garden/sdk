from dataclasses import dataclass
from datetime import time, datetime

TIME_FORMAT = '%H:%M'


@dataclass
class DeviceState:
    refill_time: time | None = None
    refill_interval: int | None = None
    max_pump_duration: str | None = None
    pump_state: bool | None = None

    def to_payload(self) -> dict[str, str]:
        payload = {}
        if self.refill_time is not None:
            payload['refillTime'] = self.refill_time.strftime('%H:%M')
        if self.refill_interval is not None:
            payload['refillInterval'] = f'{self.refill_interval}days'
        if self.max_pump_duration is not None:
            payload['maxPumpDuration'] = self.max_pump_duration
        if self.pump_state is not None:
            payload['pumpState'] = 'on' if self.pump_state else 'off'
        return payload

    @staticmethod
    def from_payload(payload: dict[str, str]) -> 'DeviceState':
        return DeviceState(
            refill_time=DeviceState.parse_refill_time(payload),
            refill_interval=DeviceState.parse_refill_interval(payload),
            max_pump_duration=DeviceState.parse_max_pump_duration(payload),
            pump_state=DeviceState.parse_pump_state(payload)
        )

    @staticmethod
    def parse_max_pump_duration(payload):
        return payload.get('maxPumpDuration')

    @staticmethod
    def parse_refill_time(payload):
        refill_time_str = payload.get('refillTime')
        return refill_time_str and datetime.strptime(refill_time_str, TIME_FORMAT).time()

    @staticmethod
    def parse_refill_interval(payload):
        refill_interval_str = payload.get('refillInterval')
        return refill_interval_str and int(refill_interval_str.replace('days', ''))

    @staticmethod
    def parse_pump_state(payload):
        pump_state_str = payload.get('pumpState')
        match pump_state_str:
            case 'on':
                return True
            case 'off':
                return False
            case None:
                return None
            case _:
                raise ValueError(f'Unknown pump state {pump_state_str}')
