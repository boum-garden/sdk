# Boum Python SDK
Status: ![GitHub Actions](https://github.com/boum-garden/sdk/actions/workflows/main.yml/badge.svg)

## Overview
This project provides an api client to interact with the [boum api](https://api.boum.us/swagger) and abstractions to 
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
from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceState

with ApiClient("email", "password") as client:
    # Get call to the devices collection
    device_ids = client.root.devices.get()

    # Get call to a specific device 
    device_states = client.root.devices(device_ids[0]).get()

    # Patch call to a specific device
    client.root.devices(device_ids[0]).patch(DeviceState())

    # Get call to a devices data
    data = client.root.devices(device_ids[0]).data.get()
```

Note that it is not possible to use multiple instances of the client at the same time. The client is a singleton and
will raise an exception if you try to instantiate it more than once.


### Resource Abstractions
The resource abstractions provide an intuitive interface to interact with the underlying resources.

```python
from datetime import time, datetime, timedelta
import pandas as pd
from boum.api_client.v1.client import ApiClient
from boum.resources.device import Device

with ApiClient("email", "password") as client:
    # Get available device ids
    device_ids = Device.get_device_ids(client)

    # Create a device instance
    device = Device(device_ids[0], client)

    # Set the pump state
    device.pump_state = True  # True for on, False for off

    # Set the refill times
    device.refill_time = time(8, 0)

    # Get the refill times
    current_refill_times = device.refill_time

    # Get device telemetry data
    data = device.get_telemetry_data(start=datetime.now() - timedelta(days=1), end=datetime.now())
    
    # Convert telemetry data to pandas dataframe
    pd.DataFrame(data)
```


## Development

### Dependecy management
[Poetry](https://python-poetry.org/) is used for depency management and publishing flow.

### Versioning
Versioning is done using [bumpver](https://pypi.org/project/bumpver/) 
with [semantic versioning](https://semver.org/)


### Testing
There are two types of tests in this repository: unit tests and contract tests.

#### Unit tests
These are completely self-contained and have no external dependencies.

#### Contract tests
These test the interactions of the SDK with the boum API. They require an instance (fake or real) of the API to run 
against



