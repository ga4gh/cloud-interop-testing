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

with open('README.md', encoding='utf-8') as description_file:
    LONG_DESCRIPTION = description_file.read()

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
    packages=find_packages(),
    package_data={'ga4ghtest': ['openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'testbed_server=ga4ghtest.__main__:main'
        ]
    },
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    platforms=['MacOS X', 'Posix'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

