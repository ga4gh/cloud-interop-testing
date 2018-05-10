#!/usr/bin/env python

import os
import sys
import setuptools.command.egg_info as egg_info_cmd
import shutil

from setuptools import setup, find_packages

SETUP_DIR = os.path.dirname(__file__)

long_description = ""

# with open("README.pypi.rst") as readmeFile:
#     long_description = readmeFile.read()

setup(
    name='synapse-orchestrator',
    version='0.1',
    description='Synapse-based orchestrator for GA4GH workflows',
    long_description=long_description,
    author='Sage Bionetworks CompOnc Team',
    author_email='james.a.eddy@gmail.com',
    url='https://github.com/Sage-Bionetworks/synevalharness',
    download_url='https://github.com/Sage-Bionetworks/synevalharness',
    license='Apache 2.0',
    packages=['synorchestrator'],
    install_requires=[
        'bravado',
        'synapseclient',
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'mock']
    entry_points={
    'console_scripts': 'orchestrate=synorchestrator.__main__:main'
    },
    zip_safe=True
)
