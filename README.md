# GA4GH Cloud Orchestrator

| **Service \ Branch** | **master** | **develop** |
| -: | - | - |
| CI status | [![Travis-CI Build Status](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator.svg?branch=master)](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator) | [![Travis-CI Build Status](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator.svg?branch=develop)](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator) |
| Test coverage | [![Coverage Status](https://coveralls.io/repos/github/Sage-Bionetworks/synapse-orchestrator/badge.svg?branch=master)](https://coveralls.io/Sage-Bionetworks/synapse-orchestrator?branch=master) | [![Coverage Status](https://coveralls.io/repos/github/Sage-Bionetworks/synapse-orchestrator/badge.svg?branch=develop)](https://coveralls.io/Sage-Bionetworks/synapse-orchestrator?branch=develop) |
| Docs status | *pending* | *pending* |

The initial use case for this app will be to act as a workflow orchestrator and bridge between TRS and WES endpoints for the [**Testbed Interoperability Platform**](https://docs.google.com/document/d/12Mq4v7o5VKF-DkFTQwsUQ-aWZ5aBeIcl_5YrhbaSv7M/edit?usp=sharing), a core deliverable of the GA4GH Cloud Workstream for 2018.

## Overview

In the context of the testbed, the orchestrator performs 3 primary tasks:

1. Look up a workflow registered in a TRS implementation, identify its corresponding "checker" workflow, and retrieve any data required to run the checker workflow;
2. Format checker workflow data and initiate new workflow runs on one or more WES endpoints;
3. Reports results.

Additionally, the application supports the following operations:

+ Register and configure new TRS endpoints;
+ Register and configure new WES endpoints;
+ Onboard/register a new workflow (by creating and configuring a queue with workflow details).

## Installation & Usage

*Coming soon...*

