# Synapse Workflow Orchestrator

This application serves as a "workflow orchestrator" for GA4GH-style workflows, using the Synapse [**Evaluation Services**](http://docs.synapse.org/rest/#org.sagebionetworks.repo.web.controller.EvaluationController) to manage queues and submissions.

## GA4GH Workflow Portability Testbed

The initial use case for this app will be to act as a workflow orchestrator for the [**Testbed Interoperability Platform**](https://docs.google.com/document/d/12Mq4v7o5VKF-DkFTQwsUQ-aWZ5aBeIcl_5YrhbaSv7M/edit?usp=sharing), a core deliverable of the GA4GH Cloud Workstream for 2018. This platform and the orchestrator will also support the next round of the **GA4GH/DREAM Workflow Execution Challenge**.

Per the requirements linked in the document above, the orchestrator needs to perform at least 3 basic tasks:

1. Makes TRS call to fetch a workflow
2. Makes WES call to run (and check) a workflow
3. Reports results

Some other obvious functionality that we'll want to include is:

+ The ability to onboard/register a new workflow (~ create and configure a queue)
+ The ability to register a new WES endpoint 
+ The ability to submit or trigger a new workflow execution job (run) 
+ A central mechanism for reporting results across workflows, WES endpoints, and specific runs/parameters 

These latter features are where existing Synapse systems come into play. Most of what we plan to do (at least for a proof of concept demonstration) can be accomplished with existing functionality of the `evaluation` API, the Synapse leaderboards, and various scripts/functions that have been designed to use these services to manage DREAM Challenges. 

### Organization 

Some rough ideas for modules:
+ **`eval_client`**: 
  + creates, configures, and gets information about Synapse evaluation queues
  + retrieves and manages information (e.g. status) about individual submissions to an evaluation queue 
+ **`trs_client`**:
  + retrieves (and possibly updates) information about a workflow from a tool registry service (e.g. Dockstore)
  + works as a `bravado` client based on the Swagger spec provided for a TRS implementation (as opposed to any CLI that might exist for that implemenation)
+ **`wes_client`**:
  + manages interactions with a workflow execution service endpoint, including submitting new workflow jobs, monitoring workflow run progress, and collecting results 
  + works as a `bravado` client based on the Swagger spec provided for a WES implementation
  + currently imported from a git submodule pointing to a fork of [@david4046's `updates-wes-0.2` branch](https://github.com/david4096/workflow-service/tree/updates-wes-0.2) of the `workflow-service` repo
+ **`orchestrator`**:
  + functions (or class with methods) to glue together the various services above
  + at minimum, should be able to (1) take a given ID/URL for a workflow registered in a given TRS implementation; (2) prepare the workflow run request, including retrieval (and formatting?) of parameters, if not provided; (3) post the workflow run request to a given WES implementation; (4) monitor and report results of the workflow run
  + authentication/authorization might need to be handled here as well
+ either within the modules above or as part of a separate `config` module, we'll need some functions for registering TRS and WES endpoints (adding them to the scope of options for the `orchestrator`)

### Development

#### Install develop branch

This software is still in pre-alpha phase, with frequent changes being made to the ["development" branch](https://github.com/Sage-Bionetworks/synevalharness/tree/develop). To work with or contribute to the latest version, clone this repo, check out the `develop` branch, and install from source. If you plan to make changes to the code, use the `-e` mode to make the installation follow the head without having to reinstall (using `conda` or `virtualenv` to create an isolated test environment is recommended).

```
git clone git://github.com/Sage-Bionetworks/synapse-orchestrator.git
cd synapse-orchestrator
git checkout develop
pip install -e .
```

#### Update `workflow-service` git submodule

When you first clone this repo or checkout the latest `develop` branch, the `workflow-service` folder may be empty. To download the submodule’s content, you can use

```
git submodule update --init --recursive
```

You should also ensure that the submodule is on the recommended branch (and install the package to make it available to `synorchestrator`):

```
cd workflow-service
git checkout updates-wes-0.2
pip install -e .
```

### Contribute changes

Switch back to the top level (`synapse-orchestrator`) folder, check out a new branch off of `develop`, edit the code, commit changes, open a pull request.

### TODO

+ get `orchestrator` working for a single workflow, TRS implementation, and WES implementation
+ add functions/arguments for configuring (registering TRS/WES endpoints, authenticating, etc.) the `orchestrator`
+ figure out how to configure and connect Synapse evaluation queues and submissions to `orchestrator`
+ update `travis.yml` to build `synapse-orchestrator` (and `workflow-service`) before running tests
