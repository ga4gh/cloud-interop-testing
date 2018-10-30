
## Basic examples with `curl`

```
curl -X POST \
 -F 'workflow_url=https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/md5sum.cwl' \
 -F 'workflow_params=@tests/testdata/md5sum.cwl.fixed.json' \
 -F 'workflow_type=CWL' \
 -F 'workflow_type_version=v1.0' \
 --trace-ascii - \
 http://0.0.0.0:8080/ga4gh/wes/v1/runs
```

<details>
 
 ```
 0087: Content-Type: multipart/form-data; boundary=--------------------
00c7: ----8ca5db76a32b2033
00dd:
<= Recv header, 23 bytes (0x17)
0000: HTTP/1.1 100 Continue
=> Send data, 378 bytes (0x17a)
0000: --------------------------8ca5db76a32b2033
002c: Content-Disposition: form-data; name="workflow_url"
0061:
0063: https://raw.githubusercontent.com/Sage-Bionetworks/workflow-inte
00a3: rop/develop/tests/testdata/md5sum.cwl
00ca: --------------------------8ca5db76a32b2033
00f6: Content-Disposition: form-data; name="workflow_params"; filename
0136: ="md5sum.cwl.fixed.json"
0150: Content-Type: application/octet-stream
0178:
=> Send data, 179 bytes (0xb3)
0000: {.  "input_file": {.        "class": "File",.        "location":
0040:  "https://raw.githubusercontent.com/Sage-Bionetworks/workflow-in
0080: terop/develop/tests/testdata/md5sum.input".    }.}.
=> Send data, 267 bytes (0x10b)
0000:
0002: --------------------------8ca5db76a32b2033
002e: Content-Disposition: form-data; name="workflow_type"
0064:
0066: CWL
006b: --------------------------8ca5db76a32b2033
0097: Content-Disposition: form-data; name="workflow_type_version"
00d5:
00d7: v1.0
00dd: --------------------------8ca5db76a32b2033--
```

</details>

## Testbed examples with Python and `requests`

| run_id | resolve_params | attach_descriptor | pack_descriptor | attach_imports |
| --- | --- | --- | ---| --- |
| e6334deed0db48eca385302fb7234cc1 | True | True | True | False |
| e4d65e8482a34ae5a100d2810312e292 | True | False | False | True |
| 21e33f90573a459184523cad13e9a18c | True | False | False | False |

#### e6334deed0db48eca385302fb7234cc1

Parts provided to `requests.request()` field `files`:
```python
[('workflow_type', u'CWL'),
 ('workflow_type_version', 'v1.0'),
 ('workflow_attachment',
  (u'checker-workflow-wrapping-workflow.cwl',
   <StringIO.StringIO instance at 0x10666e368>)),
 ('workflow_url', u'checker-workflow-wrapping-workflow.cwl'),
 ('workflow_params',
  '{"input_file": {"class": "File", "location": "https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/md5sum.input"}, "expected_md5": "00579a00e3e7fa0674428ac7049423e2"}')]
```

<details>

<summary>POST request</summary>

```
--8b6b3058f4dabffd29328f42bf277fe3
Content-Disposition: form-data; name="workflow_type"; filename="workflow_type"

CWL
--8b6b3058f4dabffd29328f42bf277fe3
Content-Disposition: form-data; name="workflow_type_version"; filename="workflow_type_version"

v1.0
--8b6b3058f4dabffd29328f42bf277fe3
Content-Disposition: form-data; name="workflow_attachment"; filename="checker-workflow-wrapping-workflow.cwl"

{
    "cwlVersion": "v1.0",
    "$graph": [
        {
            "inputs": [
                {
                    "type": "string",
                    "id": "#main/expected_md5"
                },
                {
                    "type": "File",
                    "id": "#main/input_file"
                }
            ],
            "requirements": [
                {
                    "class": "SubworkflowFeatureRequirement"
                }
            ],
            "doc": "This demonstrates how to wrap a \"real\" tool with a checker workflow that runs both the tool and a tool that performs verification of results\n",
            "id": "#main",
            "steps": [
                {
                    "out": [
                        "#main/checker/results_file"
                    ],
                    "run": "#md5sum-checker.cwl",
                    "id": "#main/checker",
                    "in": [
                        {
                            "source": "#main/expected_md5",
                            "id": "#main/checker/expected_md5"
                        },
                        {
                            "source": "#main/md5sum/output_file",
                            "id": "#main/checker/input_file"
                        }
                    ]
                },
                {
                    "out": [
                        "#main/md5sum/output_file"
                    ],
                    "run": "#md5sum-workflow.cwl",
                    "id": "#main/md5sum",
                    "in": [
                        {
                            "source": "#main/input_file",
                            "id": "#main/md5sum/input_file"
                        }
                    ]
                }
            ],
            "outputs": [
                {
                    "outputSource": "#main/checker/results_file",
                    "type": "File",
                    "id": "#main/workflow_output_file"
                }
            ],
            "class": "Workflow"
        },
        {
            "inputs": [
                {
                    "inputBinding": {
                        "position": 2,
                        "prefix": "--md5"
                    },
                    "type": "string",
                    "id": "#md5sum-checker.cwl/expected_md5"
                },
                {
                    "doc": "The file that contains an md5sum.",
                    "inputBinding": {
                        "position": 1,
                        "prefix": "--input-file"
                    },
                    "type": "File",
                    "id": "#md5sum-checker.cwl/input_file"
                }
            ],
            "requirements": [
                {
                    "dockerPull": "quay.io/agduncan94/checker-md5sum",
                    "class": "DockerRequirement"
                },
                {
                    "class": "InlineJavascriptRequirement"
                }
            ],
            "outputs": [
                {
                    "doc": "A text log file that contains more details.",
                    "outputBinding": {
                        "glob": "log.txt"
                    },
                    "type": "File",
                    "id": "#md5sum-checker.cwl/log_file"
                },
                {
                    "doc": "A json file that contains the result of the test.",
                    "outputBinding": {
                        "glob": "results.json"
                    },
                    "type": "File",
                    "id": "#md5sum-checker.cwl/results_file"
                }
            ],
            "baseCommand": [
                "/bin/check_md5sum"
            ],
            "label": "A tool that checks the md5sum workflow",
            "id": "#md5sum-checker.cwl",
            "class": "CommandLineTool",
            "hints": [
                {
                    "coresMin": 1,
                    "ramMin": 1024,
                    "class": "ResourceRequirement",
                    "outdirMin": 512000
                }
            ]
        },
        {
            "inputs": [
                {
                    "doc": "The file that will have its md5sum calculated.",
                    "inputBinding": {
                        "position": 1
                    },
                    "type": "File",
                    "id": "#md5sum-tool.cwl/input_file"
                }
            ],
            "requirements": [
                {
                    "dockerPull": "quay.io/agduncan94/my-md5sum",
                    "class": "DockerRequirement"
                },
                {
                    "class": "InlineJavascriptRequirement"
                }
            ],
            "outputs": [
                {
                    "doc": "A text file that contains a single line that is the md5sum of the input file.",
                    "outputBinding": {
                        "glob": "md5sum.txt"
                    },
                    "type": "File",
                    "id": "#md5sum-tool.cwl/output_file",
                    "format": "http://edamontology.org/data_3671"
                }
            ],
            "baseCommand": [
                "/bin/my_md5sum"
            ],
            "label": "Simple md5sum tool",
            "id": "#md5sum-tool.cwl",
            "class": "CommandLineTool",
            "hints": [
                {
                    "coresMin": 1,
                    "ramMin": 1024,
                    "class": "ResourceRequirement",
                    "outdirMin": 512
                }
            ]
        },
        {
            "id": "#md5sum-workflow.cwl",
            "inputs": [
                {
                    "type": "File",
                    "id": "#md5sum-workflow.cwl/input_file"
                }
            ],
            "steps": [
                {
                    "out": [
                        "#md5sum-workflow.cwl/md5sum/output_file"
                    ],
                    "run": "#md5sum-tool.cwl",
                    "id": "#md5sum-workflow.cwl/md5sum",
                    "in": [
                        {
                            "source": "#md5sum-workflow.cwl/input_file",
                            "id": "#md5sum-workflow.cwl/md5sum/input_file"
                        }
                    ]
                }
            ],
            "class": "Workflow",
            "outputs": [
                {
                    "outputSource": "#md5sum-workflow.cwl/md5sum/output_file",
                    "type": "File",
                    "id": "#md5sum-workflow.cwl/output_file"
                }
            ]
        }
    ]
}
--8b6b3058f4dabffd29328f42bf277fe3
Content-Disposition: form-data; name="workflow_url"; filename="workflow_url"

checker-workflow-wrapping-workflow.cwl
--8b6b3058f4dabffd29328f42bf277fe3
Content-Disposition: form-data; name="workflow_params"; filename="workflow_params"

{"input_file": {"class": "File", "location": "https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/md5sum.input"}, "expected_md5": "00579a00e3e7fa0674428ac7049423e2"}
--8b6b3058f4dabffd29328f42bf277fe3--
```

</details>

#### e4d65e8482a34ae5a100d2810312e292

Parts provided to `requests.request()` field `files`:
```python
[('workflow_type', u'CWL'),
 ('workflow_type_version', 'v1.0'),
 ('workflow_url',
  u'https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/checker-workflow-wrapping-workflow.cwl'),
 ('workflow_params',
  '{"input_file": {"class": "File", "location": "https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/md5sum.input"}, "expected_md5": "00579a00e3e7fa0674428ac7049423e2"}'),
 ('workflow_attachment',
  (u'md5sum/md5sum-workflow.cwl',
   <StringIO.StringIO instance at 0x1098f6a28>)),
 ('workflow_attachment',
  (u'md5sum/md5sum-tool.cwl', <StringIO.StringIO instance at 0x10666f638>)),
 ('workflow_attachment',
  (u'checker/md5sum-checker.cwl',
   <StringIO.StringIO instance at 0x1098739e0>))]
```

<details>

<summary>POST request</summary>

```
--bfa2e048cff71fa3f72da218f372d094
Content-Disposition: form-data; name="workflow_type"; filename="workflow_type"

CWL
--bfa2e048cff71fa3f72da218f372d094
Content-Disposition: form-data; name="workflow_type_version"; filename="workflow_type_version"

v1.0
--bfa2e048cff71fa3f72da218f372d094
Content-Disposition: form-data; name="workflow_url"; filename="workflow_url"

https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/checker-workflow-wrapping-workflow.cwl
--bfa2e048cff71fa3f72da218f372d094
Content-Disposition: form-data; name="workflow_params"; filename="workflow_params"

{"input_file": {"class": "File", "location": "https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/md5sum.input"}, "expected_md5": "00579a00e3e7fa0674428ac7049423e2"}
--bfa2e048cff71fa3f72da218f372d094
Content-Disposition: form-data; name="workflow_attachment"; filename="md5sum/md5sum-workflow.cwl"

cwlVersion: v1.0
class: Workflow

inputs:
  input_file: File

outputs:
  output_file:
    type: File
    outputSource: md5sum/output_file

steps:
  md5sum:
    run: md5sum-tool.cwl
    in:
      input_file: input_file
    out: [output_file]

--bfa2e048cff71fa3f72da218f372d094
Content-Disposition: form-data; name="workflow_attachment"; filename="md5sum/md5sum-tool.cwl"

#!/usr/bin/env cwl-runner

class: CommandLineTool
id: Md5sum
label: Simple md5sum tool
cwlVersion: v1.0

$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/

requirements:
- class: DockerRequirement
  dockerPull: quay.io/agduncan94/my-md5sum
- class: InlineJavascriptRequirement

hints:
- class: ResourceRequirement
  # The command really requires very little resources.
  coresMin: 1
  ramMin: 1024
  outdirMin: 512

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
    doc: The file that will have its md5sum calculated.

outputs:
  output_file:
    type: File
    format: http://edamontology.org/data_3671
    outputBinding:
      glob: md5sum.txt
    doc: A text file that contains a single line that is the md5sum of the input file.

baseCommand: [/bin/my_md5sum]

--bfa2e048cff71fa3f72da218f372d094
Content-Disposition: form-data; name="workflow_attachment"; filename="checker/md5sum-checker.cwl"

#!/usr/bin/env cwl-runner

class: CommandLineTool
id: Md5sumWorkflowChecker
label: A tool that checks the md5sum workflow
cwlVersion: v1.0

requirements:
- class: DockerRequirement
  dockerPull: quay.io/agduncan94/checker-md5sum
- class: InlineJavascriptRequirement

hints:
- class: ResourceRequirement
  # The command really requires very little resources.
  coresMin: 1
  ramMin: 1024
  outdirMin: 512000

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      prefix: --input-file
    doc: The file that contains an md5sum.
  expected_md5:
    type: string
    inputBinding:
      position: 2
      prefix: --md5


outputs:
  results_file:
    type: File
    outputBinding:
      glob: results.json
    doc: A json file that contains the result of the test.

  log_file:
    type: File
    outputBinding:
      glob: log.txt
    doc: A text log file that contains more details.

baseCommand: [/bin/check_md5sum]

--bfa2e048cff71fa3f72da218f372d094--
```

</details>


#### 21e33f90573a459184523cad13e9a18c

Parts provided to `requests.request()` field `files`:

```python
[('workflow_type', u'CWL'),
 ('workflow_type_version', 'v1.0'),
 ('workflow_url',
  u'https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/checker-workflow-wrapping-workflow.cwl'),
 ('workflow_params',
  '{"input_file": {"class": "File", "location": "https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/md5sum.input"}, "expected_md5": "00579a00e3e7fa0674428ac7049423e2"}')]
```

<details>

<summary>POST request</summary>

```
--1d351b6fc2deba11c6764a47d1af9185
Content-Disposition: form-data; name="workflow_type"; filename="workflow_type"

CWL
--1d351b6fc2deba11c6764a47d1af9185
Content-Disposition: form-data; name="workflow_type_version"; filename="workflow_type_version"

v1.0
--1d351b6fc2deba11c6764a47d1af9185
Content-Disposition: form-data; name="workflow_url"; filename="workflow_url"

https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/checker-workflow-wrapping-workflow.cwl
--1d351b6fc2deba11c6764a47d1af9185
Content-Disposition: form-data; name="workflow_params"; filename="workflow_params"

{"input_file": {"class": "File", "location": "https://raw.githubusercontent.com/dockstore-testing/md5sum-checker/develop/md5sum.input"}, "expected_md5": "00579a00e3e7fa0674428ac7049423e2"}
--1d351b6fc2deba11c6764a47d1af9185--
```

</details>
