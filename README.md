# Synapse Workflow Orchestrator

| **Service \ Branch** | **master** | **develop** |
| -: | - | - |
| CI status | [![Travis-CI Build Status](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator.svg?branch=master)](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator) | [![Travis-CI Build Status](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator.svg?branch=develop)](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator) |
| Test coverage | [![Coverage Status](https://coveralls.io/repos/github/Sage-Bionetworks/synapse-orchestrator/badge.svg?branch=master)](https://coveralls.io/Sage-Bionetworks/synapse-orchestrator?branch=master) | [![Coverage Status](https://coveralls.io/repos/github/Sage-Bionetworks/synapse-orchestrator/badge.svg?branch=develop)](https://coveralls.io/Sage-Bionetworks/synapse-orchestrator?branch=develop) |
| Docs status | *pending* | *pending* |

This application serves as a "workflow orchestrator" for GA4GH-style workflows, using the Synapse [**Evaluation Services**](http://docs.synapse.org/rest/#org.sagebionetworks.repo.web.controller.EvaluationController) to manage queues and submissions.

## GA4GH Workflow Portability Testbed

The initial use case for this app will be to act as a workflow orchestrator for the [**Testbed Interoperability Platform**](https://docs.google.com/document/d/12Mq4v7o5VKF-DkFTQwsUQ-aWZ5aBeIcl_5YrhbaSv7M/edit?usp=sharing), a core deliverable of the GA4GH Cloud Workstream for 2018. This platform and the orchestrator will also support the next round of the **GA4GH/DREAM Workflow Execution Challenge**.

Per the requirements linked in the document above, the orchestrator needs to perform at least 3 basic tasks:

1. Makes TRS call to fetch a workflow
2. Makes WES call to run (and check) a workflow
3. Reports results

Some other obvious functionality that we'll want to include (that we haven't necessarily implemented yet):

+ The ability to onboard/register a new workflow (~ create and configure a queue)
+ The ability to register a new WES endpoint 
+ The ability to submit or trigger a new workflow execution job (run) 
+ A central mechanism for reporting results across workflows, WES endpoints, and specific runs/parameters 

These latter features are where existing Synapse systems come into play. Most of what we plan to do (at least for a proof of concept demonstration) can be accomplished with existing functionality of the `evaluation` API, the Synapse leaderboards, and various scripts/functions that have been designed to use these services to manage DREAM Challenges. 

### Organization 

Current modules:
+ **`eval`**: 
  + creates, configures, and gets information about Synapse evaluation queues
  + retrieves and manages information (e.g. status) about individual submissions to an evaluation queue
  + currently just stubs and stores submissions and queues locally — Synapse integration coming soon
+ **`trs`**:
  + acts as a lightweight client for the TRS API
  + retrieves (and possibly updates) information about a workflow from a tool registry service (e.g. Dockstore)
  + submits `requests` based on a subset of the Swagger spec for the GA4GH  Tool Registry Service schema (as opposed to any CLI that might exist for a TRS implemenation)
+ **`wes`**:
  + acts as a lightweight client for the WES API
  + manages interactions with a workflow execution service endpoint, including submitting new workflow jobs, monitoring workflow run progress, and collecting results 
  + submits `requests` based on a subset of the Swagger spec for the GA4GH Workflow Execution Service schema
+ **`orchestrator`**:
  + functions to glue together the various services above
  + currently able to (1) take a given ID/URL for a workflow registered in a given TRS implementation; (2) prepare the workflow run request, including retrieval (and formatting) of parameters, if not provided; (3) post the workflow run request to a given WES implementation; (4) monitor and report results of the workflow run
  + authentication/authorization might need to be handled here as well
+ **`config`**: 
  + includes functions for registering TRS and WES endpoints (adding them to the scope of options for the `orchestrator`)
  + should eventually include more functionality for specifying the parameters of individual evaluation queues and endpoints

### Development

This software is still in pre-alpha phase, with frequent changes being made to the ["development" branch](https://github.com/Sage-Bionetworks/synapse-orchestrator/tree/develop). To work with or contribute to the latest version, clone this repo, check out the `develop` branch (if not active by default), and install from source. If you plan to make changes to the code, use the `-e` mode to make the installation follow the head without having to reinstall (using `conda` or `virtualenv` to create an isolated test environment is recommended).

(example environment setup)
```
conda create -n synorchestrator python=2.7
source activate synorchestrator
```

```
git clone git://github.com/Sage-Bionetworks/synapse-orchestrator.git
cd synapse-orchestrator
pip install -e .
```

### Contribute changes

Switch back to the top level (`synapse-orchestrator`) folder, check out a new branch off of `develop`, edit the code, commit changes, open a pull request.

### TODO

+ add functions/arguments for configuring (registering TRS/WES endpoints, authenticating, etc.) the `orchestrator`
+ figure out how to configure and connect Synapse evaluation queues and submissions to `orchestrator`
+ update `travis.yml` to build `synapse-orchestrator` (and `workflow-service`) before running tests
