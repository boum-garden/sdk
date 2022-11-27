import doctest

import boum.resources.device
from tests.contract_tests.fixtures import EMAIL, PASSWORD


def test__docstrings():
    execution_context = {
        'email': EMAIL,
        'password': PASSWORD,
    }
    doctest.testmod(
        boum.resources.device, raise_on_error=True, verbose=True, globs=execution_context)
