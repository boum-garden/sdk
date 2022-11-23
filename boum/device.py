from datetime import datetime, time


class Device:
    """Abstration over the device api client to easily interact with devices.
    """

    def __init__(self, device_id: str):
        self.device_id = device_id
        self._pump_times: list[time] = []

    @property
    def pump_times(self) -> list[time]:
        """Returns the pump times for a device

        Returns:
            list[time]: A list of times between 0:0:0 and 23:59:00
        """
        # TODO implement
        pass

    @pump_times.setter
    def pump_times(self, pump_times: list[time]):
        """Sets the pump times for a device

        Args:
            pump_times (list[time]): A list of times between 0:0:0 and 23:59:00
        """
        # TODO implement
        pass

    def get_telemetry(self, start: datetime = None, end: datetime = None) -> dict[str, list]:
        """Get telemetry data for a device

        Args:
            start (datetime): The start date of the telemetry data
            end (datetime): The end date of the telemetry data

        Returns:
            dict: The telemetry data
        """
        # TODO implement
        pass
