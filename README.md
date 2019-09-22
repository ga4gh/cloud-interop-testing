# GA4GH Cloud Interoperability Testing

[![Travis-CI Build Status](https://travis-ci.org/ga4gh/cloud-interop-testing.svg?branch=develop)](https://travis-ci.org/ga4gh/cloud-interop-testing.svg?branch=develop) 
[![Coverage Status](https://coveralls.io/repos/github/ga4gh/cloud-interop-testing/badge.svg?branch=develop)](https://coveralls.io/ga4gh/cloud-interop-testing?branch=develop)

The GA4GH Testbed Orchestrator is a system that brings together plugins that test implementations of services from the GA4GH Cloud (and eventually other) Work Stream. The orchestrator is designed to be a framework for running multiple tests within, and across services. For example, (1) the interoperability and integration tests across Workflow Execution Service (WES), Tool Registry Service (TRS), and Data Repository Service (DRS) APIs and also (2) specific compliance tests for implementations of individual APIs. By building the test infrastructure with a common Testbed Orchestrator, we can evolve how we test in the future while still leveraging a unified framework. This approach will not only make it much easier to aggregate results to a common GA4GH testing dashboard, but it will also reduce redundant code between testing efforts by factoring out orchestration to this effort.

The initial use case for this app will be to act as a workflow orchestrator and bridge between **Tool Registry Service (TRS)** and **Workflow Execution Service (WES)** endpoints for the [**Testbed Interoperability Platform**](https://docs.google.com/document/d/12Mq4v7o5VKF-DkFTQwsUQ-aWZ5aBeIcl_5YrhbaSv7M/edit?usp=sharing), a core deliverable of the GA4GH Cloud Workstream for 2018.  We're basing the design on the [GA4GH Testbed Orchestrator Design](https://docs.google.com/document/d/1Cl3EZ5B1V-nxEeUCOJKyTHHJRDhknJyopdtjNcq_7jI/edit#) document.

*Note: this repo was originally forked from [Sage-Bionetworks/workflow-interop](https://github.com/Sage-Bionetworks/workflow-interop) and will be maintained here as the testbed scope expands.*

## Overview

This is an OpenAPI-enabled (and documented) Flask server. This app uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

The (intended) logic for the testbed is further described in the in-progress [**OpenAPI specification**](https://github.com/ga4gh/cloud-interop-testing/blob/develop/ga4ghtest/openapi/openapi.yaml).


## Requirements

Python 3.6+

## Usage

To install the server and dependencies, execute the following from the root directory:

```shell
pip install -r requirements.txt . && \
  pip install --no-deps -r dev-requirements.txt
```

To start the app, you can use this command:

```shell
testbed_server
```

and open your browser to here:

```
http://localhost:8080/ga4gh/testbed/v1/ui/
```

The OpenAPI definition lives here:

```
http://localhost:8080/ga4gh/testbed/openapi.json
```

You can also find the latest version of the OpenAPI specification in GitHub [**here**](https://github.com/ga4gh/cloud-interop-testing/blob/develop/ga4ghtest/openapi/openapi.yaml).


## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t ga4ghtest .

# starting up a container
docker run -p 8080:8080 ga4ghtest
```

## Development

After editing the OpenAPI YAML spec, controller and model code can be regenerated with the following command:

```shell
bash codegen.sh
```
