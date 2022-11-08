#!/usr/bin/env python
from boum.api.utils import HttpMethods
from datetime import datetime

def validate_time_start_and_end(value):
    if isinstance(value, datetime):
        return '{}Z'.format(value.isoformat().split('.')[0])
    elif isinstance(value, str):
        if value[0] == '-' and value[-1] in ['d', 'h', 'm']:
            try:
                int(value.strip('-')[0:-1])
            except ValueError:
                raise ValueError('Invalid time format')
            return value
        else:
            raise ValueError('Invalid time format')
    else:
        raise ValueError('Invalid time format')

def validate_interval(value):
    if isinstance(value, str):
        if value[-1] in ['d', 'h', 'm']:
            try:
                int(value[0:-1])
            except ValueError:
                raise ValueError('Invalid interval format')
            return value
        else:
            raise ValueError('Invalid interval format')
    else:
        raise ValueError('Invalid interval format')

class DataMixin:
    """Mixin including methods to call data related API endpoints.
    """

    def get_device_data(self, device_id=None, time_start='-24h', time_end=None, interval='1h'):
        """Calls the user endpoint to retrieve details about a user.

        Args:
            user_id (str): The id of the user for which to provide details (required if called
                by a pipeline or an admin user)

        Returns:
            ...
        """
        interval = validate_interval(interval)
        time_start = validate_time_start_and_end(time_start)
        if time_end:
            time_end = validate_time_start_and_end(time_end)    
        headers = self._get_default_headers_with_auth()
        url = "{}/device/data/{}?timeStart={}&interval={}".format(self._base_url, device_id, time_start, interval)
        if time_end:
            url += "&timeEnd={}".format(time_end)
        # TODO return a dataframe instead of json
        return self._handle_http_request(HttpMethods.GET, url, headers=headers).json()

