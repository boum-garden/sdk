from dataclasses import dataclass
from datetime import time, datetime

TIME_FORMAT = '%H:%M'


@dataclass
class DeviceState:
    refill_time: time | None = None
    refill_interval: int | None = None
    max_pump_duration: str | None = None
    pump_state: bool | None = None

    @staticmethod
    def from_payload(payload: dict[str, str]) -> 'DeviceState':
        pump_state_str = payload['pumpState']
        match pump_state_str:
            case 'on':
                pump_state = True
            case 'off':
                pump_state = False
            case _:
                raise ValueError(f'Unknown pump state {pump_state_str}')

        refill_interval = int(payload['refillInterval'].replace('days', ''))

        return DeviceState(
            refill_time=datetime.strptime(payload['refillTime'], TIME_FORMAT).time(),
            refill_interval=refill_interval,
            max_pump_duration=payload['maxPumpDuration'],
            pump_state=pump_state
        )

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
