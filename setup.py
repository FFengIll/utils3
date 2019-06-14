#!/usr/bin/env python
from __future__ import print_function
import sys
from setuptools import setup, find_packages

from utils3 import __version__

install_requires = [
    'plyvel',
    'logbook',
]

setup(
    name='utils3',
    description='utils for python 3',
    version=__version__,
    license="MIT",
    packages=find_packages(),
    package_data={

    },
    install_requires=install_requires,
    extras_require={
        'testcases':[],
        'docs': [],
        'tests': ['pytest'],
    },
    python_requires=">=2.7, >=3.4, ",
    setup_requires=['setuptools'],
    scripts = [
        
    ],
)
