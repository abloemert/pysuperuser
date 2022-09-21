from setuptools import setup

import pysuperuser

setup(
    name='pysuperuser',
    version=pysuperuser.__version__,
    packages=['pysuperuser'],
    entry_points={
        'console_scripts': ['python-as-superuser=pysuperuser.run_python:main']
    },
)
