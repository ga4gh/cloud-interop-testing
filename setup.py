# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = 'ga4gh-testbed'
VERSION = '0.3.0'

# First, we try to use setuptools. If it's not available locally,
# we fall back on ez_setup.
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

REQUIRES = []
with open('requirements.txt') as requirements_file:
    for line in requirements_file:
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue
        pinned_version = line.split()[0]
        REQUIRES.append(pinned_version)
# [
#     'connexion==2.0.0',
#     'swagger-ui-bundle==0.0.2',
#     'python_dateutil==2.6.0'
# ]

setup(
    name=NAME,
    version=VERSION,
    description='GA4GH Testbed Orchestrator',
    license='Apache 2.0',
    author='Sage Bionetworks CompOnc Team',
    author_email='james.a.eddy@gmail.com',
    url='https://github.com/ga4gh/cloud-interop-testbed',
    keywords=['OpenAPI', 'GA4GH Testbed Orchestrator'],
    install_requires=REQUIRES,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'mock'],
    packages=['ga4ghtest'],
    package_data={'ga4ghtest': ['openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'testbed_server=ga4ghtest.__main__:main'
        ]
    },
    long_description='''\
    The GA4GH Testbed Orchestrator is a system that brings together plugins that test implementations of services from the GA4GH Cloud (and eventually other) Work Stream. The orchestrator is designed to be a framework for running multiple tests within, and across services. For example, 1) the interoperability and integration tests across Workflow Execution Service (WES), Tool Registry Service (TRS), and Data Repository Service (DRS) APIs and also 2) specific compliance tests for implementations of individual APIs. By building the test infrastructure with a common Testbed Orchestrator, we can evolve how we test in the future while still leveraging a unified framework. This approach will not only make it much easier to aggregate results to a common GA4GH testing dashboard, but it will also reduce redundant code between testing efforts by factoring out orchestration to this effort.
    '''
)

