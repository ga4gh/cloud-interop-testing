# synevalharness
Sandbox for testing workflow execution through the Synapse evaluation API

## GA4GH Workflow Portability Testbed

The initial use case for this code will be to act as a "workflow orchestrator" for the [**Testbed Interoperability Platform**](https://docs.google.com/document/d/12Mq4v7o5VKF-DkFTQwsUQ-aWZ5aBeIcl_5YrhbaSv7M/edit?usp=sharing), a core deliverable of the GA4GH Cloud Workstream for 2018. This platform and the orchestrator will also support the next round of the **GA4GH/DREAM Workflow Execution Challenge**.

Per the requirements linked in the document above, the orchestrator needs to perform at least 3 basic tasks:

1. Makes TRS call to fetch a workflow
2. Makes WES call to run (and check) a workflow
3. Reports results

