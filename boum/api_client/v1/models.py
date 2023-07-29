from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time, datetime

from dateutil import parser
import regex as re

TIME_FORMAT = '%H:%M'
FIRMWARE_VERSION_REGEX = "^(?:(\\d+)\\.)?(?:(\\d+)\.)?(\\*|\\d+)$"
DEVICE_ID_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
DEVICE_COMMANDS = [
    "resetWiFiCredentials",
    "updateCertificate",
    "restartDevice",
    "distUsIncrStrength",
    "distUsDecrStrength",
    "distUsReadStrength",
    "distUsCleanLoop",
]

class Model(ABC):

    @abstractmethod
    def to_payload(self) -> dict[str, any]:
        """Convert the model to a dictionary with strings as keys and any type as values."""

    @staticmethod
    @abstractmethod
    def from_payload(payload: dict[str, any]) -> 'Model':
        """Convert a dictionary with strings as keys values to a model."""


@dataclass
class UserModel(Model):
    data: dict | None = None

    def to_payload(self) -> dict[str, any]:
        payload = {}
        if self.data is not None:
            payload = self.data
        return payload

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'UserModel':
        return UserModel(
            data=payload
        )

@dataclass
class DeviceLogModel(Model):
    type: str | None = None
    level: str | None = None
    message: str | None = None
    payload: dict | None = None
    device_id: str | None = None
    firmware_version: str | None = None

    def __post_init__(self):
        """Value validation after initialization"""
        if not isinstance(self.level, str | None) or not self.level in ['error', 'info', 'warning', 'debug']:
            raise ValueError('level must be a string and one of error, info, warning, debug')
        if not isinstance(self.message, str | None):
            raise ValueError('message must be a string')
        if not isinstance(self.payload, dict | None):
            raise ValueError('payload must be a dict')
        if not isinstance(self.device_id, str | None) or not re.match(DEVICE_ID_REGEX, self.device_id):
            raise ValueError('device_id must be a string and be in the format XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')
        if self.firmware_version:
            if not isinstance(self.firmware_version, str):
                if not re.match(FIRMWARE_VERSION_REGEX, self.firmware_version):
                    raise ValueError('firmware_version must be a string and be in the format MAJOR.MINOR.PATCH')

    def to_payload(self) -> dict[str, any]:
        payload = {}
        if self.type is not None:
            payload['type'] = self.type
        if self.level is not None:
            payload['level'] = self.level
        if self.message is not None:
            payload['message'] = self.message
        if self.payload is not None:
            payload['payload'] = self.payload
        if self.device_id is not None:
            payload['device_id'] = self.device_id
        if self.firmware_version is not None:
            payload['firmware_version'] = self.firmware_version
        return payload

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'DeviceLogModel':
        return DeviceLogModel(
            type=payload.get('type'),
            level=payload.get('level'),
            message=payload.get('message'),
            payload=payload.get('payload'),
            device_id=payload.get('device_id'),
            firmware_version=payload.get('firmware_version')
        )
    
@dataclass
class DeviceStateModel(Model):
    refill_time: time | None = None
    refill_interval_days: int | None = None
    max_pump_duration_minutes: int | None = None
    firmware_version: str | None = None
    pump_state: bool | None = None
    device_commands: list | None = None

    def __post_init__(self):
        """Value validation after initialization"""
        if not isinstance(self.refill_time, time | None):
            raise ValueError('refill_time must be a time object or None')
        if not isinstance(self.refill_interval_days, int | None):
            raise ValueError('refill_interval_days must be an int or None')
        if self.refill_interval_days is not None and self.refill_interval_days <= 0:
            raise ValueError('refill_intervall must be positive')
        if not isinstance(self.max_pump_duration_minutes, int | None):
            raise ValueError('max_pump_duration_minutes must be an int or None')
        if self.max_pump_duration_minutes is not None and \
                not 0 < self.max_pump_duration_minutes < 24 * 60 - 1:
            raise ValueError('max_pump_duration_minutes must be between 0 and 1439 or None')
        if not isinstance(self.pump_state, bool | None):
            raise ValueError('pump_state must be a bool or None')
        if not isinstance(self.firmware_version, str | None):
            if isinstance(self.firmware_version, str) and not re.match(FIRMWARE_VERSION_REGEX, self.firmware_version):
                raise ValueError('firmware_version must be a string and be in the format MAJOR.MINOR.PATCH')        
        if not isinstance(self.device_commands, list | None):
            for command in self.device_commands:
                if not isinstance(command, str) or not command in DEVICE_COMMANDS:
                    raise ValueError('device_commands must be a list or None and contain only valid commands')    

    def to_payload(self) -> dict[str, any]:
        payload = {}
        if self.refill_time is not None:
            payload['refillTime'] = self.refill_time.strftime('%H:%M')
        if self.refill_interval_days is not None:
            payload['refillInterval'] = f'{self.refill_interval_days}days'
        if self.max_pump_duration_minutes is not None:
            payload['maxPumpDuration'] = f'{self.max_pump_duration_minutes}min'
        if self.pump_state is not None:
            payload['pumpState'] = 'on' if self.pump_state else 'off'
        if self.firmware_version is not None:
            payload['firmwareVersion'] = self.firmware_version
        if self.device_commands is not None:
            payload['deviceCommands'] = self.device_commands
        return payload

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'DeviceStateModel':
        return DeviceStateModel(
            refill_time=DeviceStateModel._parse_refill_time(payload),
            refill_interval_days=DeviceStateModel._parse_refill_interval(payload),
            max_pump_duration_minutes=DeviceStateModel._parse_max_pump_duration(payload),
            pump_state=DeviceStateModel._parse_pump_state(payload),
            firmware_version=payload.get('firmwareVersion'),
            device_commands=payload.get('deviceCommands')
        )

    @staticmethod
    def _parse_max_pump_duration(payload) -> int | None:
        max_pump_duration_str = payload.get('maxPumpDuration')
        return max_pump_duration_str and int(max_pump_duration_str.replace('min', ''))

    @staticmethod
    def _parse_refill_time(payload) -> time | None:
        refill_time_str = payload.get('refillTime')
        return refill_time_str and datetime.strptime(refill_time_str, TIME_FORMAT).time()

    @staticmethod
    def _parse_refill_interval(payload) -> int | None:
        refill_interval_str = payload.get('refillInterval')
        return refill_interval_str and int(refill_interval_str.replace('days', ''))

    @staticmethod
    def _parse_pump_state(payload) -> bool | None:
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

@dataclass
class DeviceFlagsModel(Model):
    poor_us: int | None = None
    poor_wifi: int | None = None
    draws_air: int | None = None
    water_leakage: int | None = None
    low_battery: int | None = None
    slow_recharge: int | None = None
    high_water_usage: int | None = None
    low_water_usage: int | None = None
    offline_warning: int | None = None

    def __post_init__(self):
        """Value validation after initialization"""
        if not isinstance(self.poor_us, int | None):
            raise ValueError('poor_us must be a int or None')
        if not isinstance(self.poor_wifi, int | None):
            raise ValueError('poor_wifi must be a int or None')
        if not isinstance(self.draws_air, int | None):
            raise ValueError('draws_air must be a int or None')
        if not isinstance(self.water_leakage, int | None):
            raise ValueError('water_leakage must be a int or None')
        if not isinstance(self.low_battery, int | None):
            raise ValueError('low_battery must be a int or None')
        if not isinstance(self.slow_recharge, int | None):
            raise ValueError('slow_recharge must be a int or None')
        if not isinstance(self.high_water_usage, int | None):
            raise ValueError('high_water_usage must be a int or None')
        if not isinstance(self.low_water_usage, int | None):
            raise ValueError('low_water_usage must be a int or None')
        if not isinstance(self.offline_warning, int | None):
            raise ValueError('offline_warning must be a int or None')

    def to_payload(self) -> dict[str, any]:
        payload = {}
        if self.poor_us is not None:
            payload['poorUS'] = self.poor_us
        if self.poor_wifi is not None:
            payload['poorWiFi'] = self.poor_wifi
        if self.draws_air is not None:
            payload['drawsAir'] = self.draws_air
        if self.water_leakage is not None:
            payload['waterLeakage'] = self.water_leakage
        if self.low_battery is not None:
            payload['lowBattery'] = self.low_battery
        if self.slow_recharge is not None:
            payload['slowRecharge'] = self.slow_recharge
        if self.high_water_usage is not None:
            payload['highWaterUsage'] = self.high_water_usage
        if self.low_water_usage is not None:
            payload['lowWaterUsage'] = self.low_water_usage
        if self.offline_warning is not None:
            payload['offlineWarning'] = self.offline_warning
        return payload

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'DeviceFlagsModel':
        return DeviceFlagsModel(
            poor_us=payload.get('poorUS'),
            poor_wifi=payload.get('poorWiFi'),
            draws_air=payload.get('drawsAir'),
            water_leakage=payload.get('waterLeakage'),
            low_battery=payload.get('lowBattery'),
            slow_recharge=payload.get('slowRecharge'),
            high_water_usage=payload.get('highWaterUsage'),
            low_water_usage=payload.get('lowWaterUsage'),
            offline_warning=payload.get('offlineWarning')
        )
    

@dataclass
class DeviceModel(Model):
    desired_state: DeviceStateModel | None = None
    reported_state: DeviceStateModel | None = None
    flags: DeviceFlagsModel | None = None

    def to_payload(self) -> dict[str, any]:
        payload = {'state': {}, 'flags': {}}
        if self.desired_state:
            payload['state']['desired'] = self.desired_state.to_payload()
        if self.reported_state:
            payload['state']['reported'] = self.reported_state.to_payload()
        if self.flags:
            payload['flags'] = self.flags.to_payload()
        return payload

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'DeviceModel':
        desired_dict = payload.get('state').get('desired')
        desired = None if desired_dict is None else DeviceStateModel.from_payload(desired_dict)
        reported_dict = payload.get('state').get('reported')
        reported = None if desired_dict is None else DeviceStateModel.from_payload(reported_dict)
        flags_dict = payload.get('flags')
        flags = None if flags_dict is None else DeviceFlagsModel.from_payload(flags_dict)
        return DeviceModel(desired, reported, flags)


@dataclass
class DeviceDataModel(Model):
    data: dict[str, any]

    def __post_init__(self):
        """Value validation after initialization"""
        if not isinstance(self.data, dict):
            raise ValueError('data must be a dict')
        for k, v in self.data.items():
            if not isinstance(k, str):
                raise ValueError('data keys must be strings')
            if not isinstance(v, list):
                raise ValueError(
                    'data values must be lists of strings, numeric values, bools or date/time '
                    'objects')

    def to_payload(self) -> dict[str, any]:
        raise NotImplementedError('DeviceDataModel does not support to_payload')

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'DeviceDataModel':
        device_ids = DeviceDataModel._parse_device_ids(payload)
        timestamps = DeviceDataModel._parse_timestamps(payload)
        data = DeviceDataModel._parse_values(payload)
        data['deviceId'] = device_ids
        data['timestamp'] = timestamps
        return DeviceDataModel(data)

    @staticmethod
    def _parse_timestamps(payload: dict) -> list[datetime]:
        first_timeseries = list(payload['timeSeries'].values())[0]
        timestamps = [v['x'] for v in first_timeseries]
        return [parser.isoparse(t) for t in timestamps]

    @staticmethod
    def _parse_device_ids(payload: dict) -> list[str]:
        device_id = payload['details']['deviceId']
        first_timeseries = list(payload['timeSeries'].values())[0]
        return [device_id] * len(first_timeseries)

    @staticmethod
    def _parse_values(payload: dict) -> dict[str, list[any]]:
        def tryparse_float(value: str) -> float | None:
            try:
                return float(value)
            except TypeError:
                return None
            except ValueError:
                return None

        values = {}
        for name, data in payload['timeSeries'].items():
            values[name] = [tryparse_float(v['y']) for v in data]
        return values
