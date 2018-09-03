# GA4GH Workflow Interoperability

| **Service \ Branch** | **master** | **develop** |
| -: | - | - |
| CI status | [![Travis-CI Build Status](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator.svg?branch=master)](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator) | [![Travis-CI Build Status](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator.svg?branch=develop)](https://travis-ci.org/Sage-Bionetworks/synapse-orchestrator) |
| Test coverage | [![Coverage Status](https://coveralls.io/repos/github/Sage-Bionetworks/synapse-orchestrator/badge.svg?branch=master)](https://coveralls.io/Sage-Bionetworks/synapse-orchestrator?branch=master) | [![Coverage Status](https://coveralls.io/repos/github/Sage-Bionetworks/synapse-orchestrator/badge.svg?branch=develop)](https://coveralls.io/Sage-Bionetworks/synapse-orchestrator?branch=develop) |


The initial use case for this app will be to act as a workflow orchestrator and bridge between **Tool Registry Service (TRS)** and **Workflow Execution Service (WES)** endpoints for the [**Testbed Interoperability Platform**](https://docs.google.com/document/d/12Mq4v7o5VKF-DkFTQwsUQ-aWZ5aBeIcl_5YrhbaSv7M/edit?usp=sharing), a core deliverable of the GA4GH Cloud Workstream for 2018.

## Overview

In the context of the testbed, the orchestrator performs 3 primary tasks:

1. Look up a workflow registered in a TRS implementation, identify its corresponding "checker" workflow, and retrieve any data required to run the checker workflow;
2. Format checker workflow data and initiate new workflow runs on one or more WES endpoints;
3. Reports results.

Additionally, the application supports the following operations:

+ Register and configure new TRS endpoints;
+ Register and configure new WES endpoints;
+ Onboard/register a new workflow (by creating and configuring a queue with workflow details).

## Installation

*Coming soon...*


## Usage

### Default settings

```python
from synorchestrator import config

config.show()
```

```console
Orchestrator options:

Workflow Evaluation Queues
(queue ID: workflow ID [version])
---------------------------------------------------------------------------
queue_1: None (None)
  > workflow URL: file://tests/testdata/md5sum.cwl
  > workflow type: CWL
  > from TRS: None
  > WES options: ['local']

Tool Registries
(TRS ID: host address)
---------------------------------------------------------------------------
dockstore: dockstore.org:8443

Workflow Services
(WES ID: host address)
---------------------------------------------------------------------------
local: 0.0.0.0:8080
```

<details>

<summary>View YAML</summary>

```yaml
queues:
  queue_1:
    trs_id: null
    version_id: null
    wes_default: local
    wes_opts:
    - local
    workflow_attachments:
    - file://tests/testdata/md5sum.input
    - file://tests/testdata/dockstore-tool-md5sum.cwl
    workflow_id: null
    workflow_type: CWL
    workflow_url: file://tests/testdata/md5sum.cwl
toolregistries:
  dockstore:
    auth: null
    auth_type: null
    host: dockstore.org:8443
    proto: https
workflowservices:
  local:
    auth: null
    auth_type: null
    host: 0.0.0.0:8080
    proto: http
```

</details>

### Add a workflow

```python
config.add_queue(queue_id='queue_2',
                 wf_type='CWL',
                 wf_id='github.com/dockstore-testing/md5sum-checker',
                 version_id='develop',
                 trs_id='dockstore')
```

```console
Workflow Evaluation Queues
(queue ID: workflow ID [version])
---------------------------------------------------------------------------
queue_2: github.com/dockstore-testing/md5sum-checker (develop)
  > workflow URL: None
  > workflow type: CWL
  > from TRS: dockstore
  > WES options: ['local']
queue_1: None (None)
  > workflow URL: file://tests/testdata/md5sum.cwl
  > workflow type: CWL
  > from TRS: None
  > WES options: ['local']

...
```

<details>

<summary>View YAML</summary>

```yaml
queue_2:
  trs_id: dockstore
  version_id: develop
  wes_default: local
  wes_opts:
  - local
  workflow_attachments: null
  workflow_id: github.com/dockstore-testing/md5sum-checker
  workflow_type: CWL
  workflow_url: null
```

</details>

### Add a WES endpoint

```python
config.add_workflowservice(service='arvados-wes',
                           host='wes.qr1hi.arvadosapi.com',
                           auth='<my-api-token>',
                           auth_type='token',
                           proto='https')
```

```console
Workflow Services
(WES ID: host address)
---------------------------------------------------------------------------
arvados-wes: wes.qr1hi.arvadosapi.com
local: 0.0.0.0:8080
```

#### Connect a WES endpoint to a workflow queue

```python
config.add_wes_opt(queue_ids='queue_2', wes_ids='arvados-wes')
```

```console
Workflow Evaluation Queues
(queue ID: workflow ID [version])
---------------------------------------------------------------------------
queue_2: github.com/dockstore-testing/md5sum-checker (develop)
  > workflow URL: None
  > workflow type: CWL
  > from TRS: dockstore
  > WES options: ['local', 'arvados-wes']
```

### Running workflows

In a seperate terminal window or notebook, you can start a `monitor` process to keep track of any active workflow jobs.

```python
from synorchestrator import orchestrator

orchestrator.monitor()
```
#### Check a workflow

To check a workflow in the testbed...

```python
from synorchestrator import testbed

testbed.check_workflow(queue_id='queue_2', wes_id='local')
```

#### Run a workflow job

To run a workflow using a given set of parameters...

```python
from synorchestrator import orchestrator

orchestrator.run_job(queue_id='queue_1',
                     wes_id='local',
                     wf_jsonyaml='file://tests/testdata/md5sum.cwl.json')
```
