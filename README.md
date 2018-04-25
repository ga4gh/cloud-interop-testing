# synevalharness
Sandbox for testing workflow execution through the Synapse evaluation API

## GA4GH Workflow Portability Testbed

The initial use case for this code will be to act as a "workflow orchestrator" for the [**Testbed Interoperability Platform**](https://docs.google.com/document/d/12Mq4v7o5VKF-DkFTQwsUQ-aWZ5aBeIcl_5YrhbaSv7M/edit?usp=sharing), a core deliverable of the GA4GH Cloud Workstream for 2018. This platform and the orchestrator will also support the next round of the **GA4GH/DREAM Workflow Execution Challenge**.

Per the requirements linked in the document above, the orchestrator needs to perform at least 3 basic tasks:

1. Makes TRS call to fetch a workflow
2. Makes WES call to run (and check) a workflow
3. Reports results

This is actually pretty simple, and is more or less possible now using examples from Abraham Chavez for working with Consonance and WES. Some other obvious functionality that we'll want to include is:

+ The ability to onboard/register a new workflow 
+ The ability to register a new WES endpoint 
+ The ability to submit or trigger a new workflow execution job (run) 
+ A central mechanism for reporting results across workflows, WES endpoints, and specific runs/parameters 

These latter features are where existing Synapse systems come into play. Most of what we plan to do (at least for a proof of concept demonstration) can be accomplished with existing functionality of the `evaluation`and `submission` APIs, the Synapse leaderboards, and various scripts/functions that have been designed to use these services to manage DREAM Challenges. 

### Organization 

Some rough ideas for modules (not actual names):
+ evaluation client - creates, configures, and gets information about Synapse evaluation queues 
+ submission client - retrieves and manages information (e.g. status) about individual submissions to an evaluation queue 
+ TRS client - retrieves (and possibly updates) information about a workflow from a tool registry service (e.g. Dockstore) 
+ WES client - manages interactions with a workflow execution service endpoint, including submitting new workflow jobs, monitoring workflow run progress, and collecting results 
