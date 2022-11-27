import doctest

from tests.contract_tests.fixtures import EMAIL, PASSWORD


def test__examples():
    execution_context = {
        'email': EMAIL,
        'password': PASSWORD,
    }
    doctest.testfile('../../README.md', raise_on_error=True, verbose=True, globs=execution_context)
