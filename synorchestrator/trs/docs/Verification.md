# Verifying a test parameter file

1. Go to https://staging.dockstore.org/static/swagger-ui/index.html#/extendedGA4GH/toolsIdVersionsVersionIdTypeTestsPost
2. Click "Try it now"
3. Provide a "type", this should be self-explanatory.  See the description for allowable values.
4. Provide the TRS ID for the tool/workflow being verified.  
For example, the [dockstore-tool-md5sum](https://dockstore.org/containers/quay.io/briandoconnor/dockstore-tool-md5sum:master?tab=info) tool has the TRS ID: "quay.io/briandoconnor/dockstore-tool-md5sum" as shown in the "Info" tab with the label: "TRS CWL Path" or "TRS WDL Path"
5. Provide the version_id of the tool/workflow to verify.  It can be any version listed in the Version tab of the tool/workflow.  
[dockstore-tool-md5sum](https://dockstore.org/containers/quay.io/briandoconnor/dockstore-tool-md5sum:master?tab=versions) has the following versions currently:
1.0.4, master, develop, 1.0.3, latest, 1.0.2, 1.0.1, and 1.0.0.
6. Provide the "relative_path" of the test parameter file being verified.  The path of the test parameter file is relative to the primary descriptor.  This path can be found using the [files endpoint](https://staging.dockstore.org/static/swagger-ui/index.html#/GA4GH/toolsIdVersionsVersionIdTypeFilesGet) or by viewing the files tab of a tool/workflow such as:
https://dockstore.org/containers/quay.io/briandoconnor/dockstore-tool-md5sum:1.0.4?tab=files and then further selecting the Test Parameter Files tab and view the right-most "File" dropdown. This relative path must be a test parameter file, providing a descriptor will not work.
7. Provide the "platform".  Some examples are: HCA, Cromwell, Arvados, etc
8. Select the "verified" status either as "true" or "false".  Use "true" to verify, "false" to "unverify".
9. Provide "metadata", this is typically the verifier's identity which can be something like "GA4GH/DREAM Challenge"
10. Lastly, provide your Dockstore token using the lock icon at the top right of the endpoint

Below is a screenshot of someone verifying the "test.json" test parameter file of the "master" version of the "dockstore-tool-md5sum" tool.  

![Swagger-UI](Swagger.png)

The curl command results in something like:

`curl -X POST "https://staging.dockstore.org/api/api/ga4gh/v2/extended/quay.io%2Fbriandoconnor%2Fdockstore-tool-md5sum/versions/master/CWL/tests/test.json?platform=Dockstore%20CLI&verified=true&metadata=Phase%201%20GA4GH%20Tool%20Execution%20Challenge" -H  "accept: application/json" -H  "Authorization: Bearer a0b1c1d8e9f9g9h8i8j1k9l9m9n1o1p9q7r2s5tuvwxyz3"`

A successful response will result in something like:

```
{
  "Dockstore CLI": {
    "metadata": "Phase 1 GA4GH Tool Execution Challenge",
    "verified": true
  }
}
```

# Viewing on Dockstore.org

There are 3 new indicators in Dockstore.org that indicates whether or not the tool/workflow is correctly verified.

To see if the verified tool/workflow is correctly displaying to others on Dockstore.org, first go to the page of the tool/workflow such as https://dockstore.org/containers/quay.io/briandoconnor/dockstore-tool-md5sum:1.0.4?tab=info.  Since this tool/workflow is correctly verified, the 3 indicators can be seen:

![Tool Page](VerifiedTool.png)

1. At the top left, the checkmark indicates that at least one of the tool/workflow's version has been verified.  In general, this tool/workflow is considered verified.  

2. At the top right, the recent versions of the tool/workflow are listed.  There is a checkmark if a specific version of the tool/workflow is verified.

3. The bottom right shows whether the currently selected/viewed version is verified.  The selected version is indicated in the URL as well as the title (e.g. quay.io/briandoconnor/dockstore-tool-md5sum:1.0.4). In this example, the version 1.0.4 is selected/viewed.  This bottom right verification box contains more details such as the platform and verifier.  This example shows that "Dockstore CLI" is the platform and "Phase 1 GA4GH Tool Execution Challenge" is the verifier.

Addition information for all verified versions can be viewed at a glance in the versions tab:

![Versions Tab](VerifiedVersionsTab.png)

Once again, the checkmarks indicate the version is verified.  Platforms which the version was verified on is displayed to the right of it.  In this case, it's "Dockstore CLI"

To see more verification information about a specific version, click the view button on the same row of the version of interest:

![Selecting in Versions Tab](SelectingVersionsTab.png)

In this example, the "master" version is selected and a modal pops up.  The bottom of it displays detailed verification information:

![Verification Table](VerifiedTable.png)

It lists the platform it was verified on, the verified source (verifier) and the test parameter file that was used.
