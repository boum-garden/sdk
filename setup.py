import os
try:
    from setuptools import setup, find_namespace_packages
except ImportError:
    from distutils.core import setup


version_file = open(os.path.join(os.path.dirname(__file__), 'VERSION'))
version = version_file.read().strip()

setup(
    description='boum',
    author='Ludwig Auer',
    url='https://github.com/boum-garden/boum',
    author_email='ludwig.auer@boum.garden',
    version=version,
    packages=find_namespace_packages(
        include=[
            'boum.*',
            'boum.api.*'
        ]
    ),
    install_requires=[
        'requests'
    ],
    name='boum'
)
