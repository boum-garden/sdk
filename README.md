# Boum Python SDK
Status: ![GitHub Actions](https://github.com/boum-garden/sdk/actions/workflows/main.yml/badge.svg)

## Overview
This project provides an api client to interact with the [Boum API](https://api.boum.us/swagger) and abstractions to 
simplify interactions with the underlying resources.


## Installation
The package is available on PyPI, and can be installed with pip or similar tools:

```bash
    python -m pip install boum
    poetry add boum
    pipenv install boum
    ...
```

## Usage

### API Client
The API client models the topology of the API and provides a class hierarchy that is organized in the same way as the 
endpoint paths. Email and password are required to use it.

```python
>>> from boum.api_client.v1.client import ApiClient
>>> from boum.api_client.v1.models.device_state import DeviceState
>>>
>>> with ApiClient(email, password, base_url=base_url) as client:
...     # Get call to the devices collection
...     evice_ids = client.root.devices.get()
...     # Get call to a specific device 
...     device_states = client.root.devices(device_id).get()
...     # Patch call to a specific device
...     client.root.devices(device_id).patch(DeviceState())
...     # Get call to a devices data
...     data = client.root.devices(device_id).data.get()

```

Note that using multiple instances of the client is not intended and will result in unexpected behavior.


### Resource Abstractions
The resource abstractions provide an intuitive interface to interact with the underlying resources.

```python
>>> from datetime import time, datetime, timedelta
>>> import pandas as pd
>>> from boum.api_client.v1.client import ApiClient
>>> from boum.resources.device import Device
>>>
>>> with ApiClient(email, password, base_url=base_url) as client:
...    # Get available device ids
...    device_ids = Device.get_device_ids(client)
...    # Create a device instance
...    device = Device(device_id, client)
...    # Set the pump state
...    device.set_pump_state(True)  # True for on, False for off 
...    # Get the pump state
...    reported, desired = device.get_pump_state()
...    # Set the refill time
...    device.set_refill_time(time(8, 0))
...    # Get the refill time
...    reported, desired = device.get_refill_time()
...    # Set the refill interval
...    device.set_refill_interval(3)
...    # Get the refill interval
...    reported, desired = device.get_refill_interval()
...    # Get device telemetry data
...    data = device.get_telemetry_data(start=datetime.now() - timedelta(days=1),
...        end=datetime.now())
...    # Convert telemetry data to pandas dataframe
...    df = pd.DataFrame(data)

```


## Development

### Dependecy management
[Poetry](https://python-poetry.org/) is used for depency management and publishing flow.

### Versioning
Versioning is done using [bumpver](https://pypi.org/project/bumpver/) 
with [semantic versioning](https://semver.org/)


### Testing

#### Unit tests
These are completely self-contained and have no external dependencies.

#### End-to-end tests
These test the entire flow from user facing python classes to the underlying api calls. They require an instance 
(fake or real) of the API to run against. They also require a registered user with a clamied device.
API Base URL, email and password are required as environmental variables.

```bash
    BOUM_SDK_TEST_BASE_URL
    BOUM_SDK_TEST_EMAIL
    BOUM_SDK_TEST_PASSWORD
```

#### Doctests

Part of the end-to-end tests are document tests executed using 
[doctest](https://docs.python.org/3/library/doctest.html). 
These tests ensure that all the examples in this README and in the docstrings are up-to-date and working.





