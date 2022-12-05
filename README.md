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
endpoint paths. Email and password or a token are required to use it.

```python
>>> from boum.api_client.v1.client import ApiClient
>>> from boum.api_client.v1.models import DeviceModel
>>> 
>>> client = ApiClient(email, password, base_url=base_url)
>>> # or ApiClient(refresh_token='token', base_url=base_url)
>>>
>>> with client:
...     # Get call to the devices collection
...     device_ids = client.root.devices.get()
...     # Get call to a specific device 
...     device_states = client.root.devices(device_id).get()
...     # Patch call to a specific device
...     client.root.devices(device_id).patch(DeviceModel())
...     # Get call to a devices data
...     data = client.root.devices(device_id).data.get()

```

Note that using multiple instances of the client is not intended and will result in unexpected behavior.


### Resource Abstractions
The resource abstractions provide a more intuitive interface to interact with the underlying resources.

```python
>>> from datetime import time, datetime, timedelta
>>> import pandas as pd
>>> from boum.api_client.v1.client import ApiClient
>>> from boum.resources.device import Device
>>> from boum.api_client.v1.models import DeviceStateModel
>>>
>>> client = ApiClient(email, password, base_url=base_url)
>>> # or ApiClient(refresh_token='token', base_url=base_url)
>>>
>>> with client:
...    # Get available device ids
...    device_ids = Device.get_device_ids(client)
...    # Create a device instance
...    device = Device(device_id, client)
...    # Remove device claim
...    # device.unclaim()
...    # Claim a device
...    # device.claim()
...    # Set desired device state
...    desired_device_State = DeviceStateModel(
...        pump_state=True,
...        refill_time=time(3, 32),
...        refill_interval=3,
...        max_pump_duration=5
...    )
...    device.set_desired_device_state(desired_device_State)
...    # Get reported and desired device state
...    reported, desired = device.get_device_states()
...    # Get device telemetry data
...    data = device.get_telemetry_data(start=datetime.now() - timedelta(days=1),
...        end=datetime.now())
...    # Convert telemetry data to pandas dataframe
...    df = pd.DataFrame(data)

```

### Loging
The SDK uses the standard python logging module.

## Development

### Dependecy management
[Poetry](https://python-poetry.org/) is used for depency management and publishing.

### Versioning
Versioning is done using [bumpver](https://pypi.org/project/bumpver/) 
with [semantic versioning](https://semver.org/)
When the version is updated, a new tag is created and pushed to the remote repository.


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
    BOUM_SDK_TEST_DEVICE_ID
    BOUM_SDK_TEST_USER_ID
```

#### Doctests

Part of the end-to-end tests are document tests executed using 
[doctest](https://docs.python.org/3/library/doctest.html). 
These tests ensure that all the examples in this README and in the docstrings are up-to-date and working.


## CI/CD

### Integration

The GitHub action workflow `.github/workflows/checks_on_push_to_branch.yml` is triggered on every push on a branch
except main. It provides the following checks:

- Unit and end-to-end/contract tests with pytest
- Linting with pylint
- Security checks with bandit

The repository settings require that all checks pass before a pull request can be merged.

### Deployment

The GitHub action workflow `.github/workflows/deploy_on_push_to_main.yml` is triggered on every push to main. It runs a
test deployment to the test PyPI repository.

The GitHub action workflow `.github/workflows/deploy_on_release.yml` is triggered on a tag with the format `v*.*.*` and
runs a deployment to the production PyPI. It is recommended to set these tags using the GitHub release feature. 


## Technical debt

- Most tests currently require an instance of the API to run against. This is not ideal and should either be replaced
  with fake instances or mocked calls.

- Creating multiple instances of the API client is not intended and will result in unexpected behavior. This should be 
  addressed by making the client a singleton.

- Doctest requires a specific format to make examples in documentation executable. This makes the examples in this
  README harder to copy and paste. 





