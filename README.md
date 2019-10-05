# GA4GH Cloud Interoperability Testing

[![Travis-CI Build Status](https://travis-ci.org/ga4gh/cloud-interop-testing.svg?branch=develop)](https://travis-ci.org/ga4gh/cloud-interop-testing)
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

## Testing with Travis CI

We've setup automatic testing with [Travis CI](https://travis-ci.org/ga4gh/cloud-interop-testing).  
You can see this site to get details on our build and testing output and the icon above shows the
status of the develop branch.

## Development

After editing the OpenAPI YAML spec, controller and model code can be regenerated with the following command (it requires `npm` to be installed):

```shell
brew install npm # or whatever way you install npm on your system
npm install @openapitools/openapi-generator-cli -g
bash codegen.sh
```
See instructions for creating new test plugins [**here**](docs/plugin.md).

## Basic Testing Lifecycle Mocking

I added some basic components to mock how this might work in the future.  The
goal is to have an automated testing happen by Travis-CI whenever files
change, such as spreadsheets that lists DRS endpoints to test.  On Travis:

1. start the orchestrator service, in this case `simple/orchestrator.py` with `FLASK_APP=orchestrator.py python -m flask run`
1. start the dashboard service, in this case `simple/dashboard.py` with `FLASK_APP=test.py python -m flask run`
1. hit multiple plugins with a JSON parameter
1. for each plugin, return a JSON result file (would be great if this was a callback to dashboard specified when submitting the test run)
1. for each result JSON file POST it to the dashboard
1. Dashboard persists this to a simple JSON aggregate file
1. the JSON aggregate file can then be rendered as an HTML report

## Feedback on Cloud Work Stream APIs

When comparing the OpenAPI spec for the different services TRS, WES, TES and DRS the following inconsistencies were observed. They should be addressed to make the APIs specs uniform and ensure that implementers don't misinterpret the spec.

### Base Path

The _basePath_ is configured in the _openAPi spec_. This is the path used in the URL of the endpoint.

|| WES |TRS | TES | DRS |
| --- | ------------- | ------------- | ------ | --- |
|BasePath| `/ga4gh/wes/v1` | `/api/ga4gh/v1` | (None) | `/ga4gh/drs/v1` |
|Implied BasePath<br>(based on common prefix)| `/ga4gh/wes/v1` | `/api/ga4gh/v1` |   `/v1` | `/ga4gh/drs/v1` |

As you can see in the above table, they are different based on the service.

### URL Conflict

The following URLs have the same resource-name, but are served from different path based on the service name. TRS uses `/metadata`, which is meant to provide similar information as `/service-info`


|| WES | TRS | TES | DRS |
| -- | -- | -- | -- | -- |
|BasePath| `/ga4gh/wes/v1` | `/api/ga4gh/v1` | `/v1/tasks` | `/ga4gh/drs/v1` |
| path | `/service-info` | `/metadata` | `/service-info` | `/service-info` |


These URLs should be standardized across the services and potentially merged and made hostname specific instead of service specific.

### Content-Type header misuse

Some services for example _DRS_, _TRS_ and _WES_ require the _content-type_ header by default. Because of this any _GET_ request also requires the _content-type_ header even though there is no payload/body.

When using swagger-ui to send the _GET_ request, it omits the content-type header. And this can result in _HTTP 415 Unsupported Media Type_ errors. The swagger generated server must be modified manually to make the _content-type_ header optional. It’s not typical to require the _content-type_ in these cases and should be removed from the openApi spec.

### Tags

The tags specified in the openApi spec are inconsistent.

|| WES | TRS | TES | DRS |
| -- | -- | -- | -- | -- |
|tags|WorkflowExecutionService|GA4GH|TaskService|DataRepositoryService|

This is a minor and mostly cosmetic change. But will make the Swagger UI more usable out of the box.
