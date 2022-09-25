from setuptools import setup

import pysuperuser

setup(
    name='pysuperuser',
    version=pysuperuser.__version__,
    packages=['pysuperuser'],
    install_requires=[
        "pywin32;os_name=='nt'",
    ],
)
