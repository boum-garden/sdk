from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time, datetime

from dateutil import parser

TIME_FORMAT = '%H:%M'


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
class DeviceStateModel(Model):
    refill_time: time | None = None
    refill_interval_days: int | None = None
    max_pump_duration_minutes: int | None = None
    pump_state: bool | None = None

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
        return payload

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'DeviceStateModel':
        return DeviceStateModel(
            refill_time=DeviceStateModel._parse_refill_time(payload),
            refill_interval_days=DeviceStateModel._parse_refill_interval(payload),
            max_pump_duration_minutes=DeviceStateModel._parse_max_pump_duration(payload),
            pump_state=DeviceStateModel._parse_pump_state(payload)
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
class DeviceModel(Model):
    desired_state: DeviceStateModel | None = None
    reported_state: DeviceStateModel | None = None

    def to_payload(self) -> dict[str, any]:
        payload = {'state': {}}
        if self.desired_state:
            payload['state']['desired'] = self.desired_state.to_payload()
        if self.reported_state:
            payload['state']['reported'] = self.reported_state.to_payload()
        return payload

    @staticmethod
    def from_payload(payload: dict[str, any]) -> 'DeviceModel':
        desired_dict = payload.get('desired')
        desired = None if desired_dict is None else DeviceStateModel.from_payload(desired_dict)
        reported_dict = payload.get('reported')
        reported = None if desired_dict is None else DeviceStateModel.from_payload(reported_dict)

        return DeviceModel(desired, reported)


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
