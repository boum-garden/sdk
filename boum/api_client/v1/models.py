from dataclasses import dataclass
from datetime import time


@dataclass
class DeviceState:
    refill_times: list[time] | None = None
    max_pump_duration: str | None = None
    pump_state: bool | None = None

    @staticmethod
    def from_payload(payload: dict[str, str]) -> 'DeviceState':
        refill_times = payload.get('refillTime')
        max_pump_duration = payload.get('maxPumpDuration')
        pump_state = payload.get('pumpState')
        return DeviceState(
            refill_times=payload['refillTime'],
            max_pump_duration=payload['maxPumpDuration'],
            pump_state=payload['pumpState']
        )

    def to_payload(self) -> dict[str, str]:
        payload = {}
        if self.refill_times is not None:
            payload['refillTime'] = self.refill_times
        if self.max_pump_duration is not None:
            payload['maxPumpDuration'] = self.max_pump_duration
        if self.pump_state is not None:
            payload['pumpState'] = 'ON' if self.pump_state else 'OFF'
        return payload
