from dataclasses import dataclass


@dataclass
class DesiredDeviceState:
    firmwareVersion: str | None
    refillTime: str | None
    maxPumpDuration: str | None
    pumpState: str | None

