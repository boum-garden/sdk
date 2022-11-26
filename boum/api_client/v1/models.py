from dataclasses import dataclass


@dataclass
class DeviceState:
    refill_time: str | None = None
    max_pump_duration: str | None = None
    pump_state: str | None = None
