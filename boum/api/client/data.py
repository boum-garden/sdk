#!/usr/bin/env python
from boum.api.utils import HttpMethods

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
        # TODO return a dataframe instead of json
        # TODO validate time_start and time_end... can beiso formatted timestamps (2021-12-22T15:00:00Z) or -24h, -7d, -1m, -1y
        headers = self._get_default_headers_with_auth()
        url = "{}/device/data/{}?timeStart={}&interval={}".format(self._base_url, device_id, time_start, interval)
        if time_end:
            url += "&timeEnd={}".format(time_end)
        return self._handle_http_request(HttpMethods.GET, url, headers=headers).json()

