# Boum Python SDK
Version: 

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
endpoint paths.

Sign in with email and password is required to use the API.

```python
from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceState

client = ApiClient()
with client("email", "password"):
    
    # Get call to the devices collection
    device = client.endpoints.devices.get()
    
    # Get call to a specific device 
    device = client.endpoints.devices('device_id').get()
    
    # Patch call to a specific device
    device = client.endpoints.devices('device_id').patch(DeviceState())
    
    # Get call to the devices data
    data = client.endpoints.devices('device_id').data.get()
    
```


### Abstractions

Todo


## Development

### Dependecy management
[Poetry](https://python-poetry.org/) is used for depency management and publishing flow.


### Versioning

Versioning is done using [bumpver](https://pypi.org/project/bumpver/) 
with [semantic versioning](https://semver.org/)



