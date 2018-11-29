import json

from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient

# Your Dockstore token (need to be a Dockstore curator, contact Dockstore team to become one)
curator_token = ""
# The Dockstore hostname(production Dockstore would be "dockstore.org")
hostname = "dockstore.org"
http_client = RequestsClient()
http_client.set_api_key(hostname, "Bearer " + curator_token, param_name="Authorization",
                        param_in="header")
# dockstore_verifier.json is a stripped down version of the Dockstore swagger.json that only has the one verification endpoint
with open('dockstore_verifier.json', 'r') as f:
    distros_dict = json.load(f)
client = SwaggerClient.from_spec(distros_dict, http_client=http_client)

# metadata will be renamed the the future as "verifier" or similar
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="CWL",
                                                                      id="#workflow/github.com/dockstore-testing/md5sum-checker",
                                                                      version_id="develop",
                                                                      relative_path="md5sum-input-cwl.json",
                                                                      platform="Arvados", verified=True,
                                                                      metadata="AGHA via Veritas").response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/dockstore-testing/md5sum-checker/wdl",
                                                                      version_id="develop",
                                                                      relative_path="md5sum-wdl.json",
                                                                      platform="Cromwell",
                                                                      metadata="TopMed, HCA via Broad",
                                                                      verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/dockstore-testing/md5sum-checker/wdl",
                                                                      version_id="develop",
                                                                      relative_path="md5sum-wdl.json", platform="Cromwell",
                                                                      metadata="GEL, AGHA via Illumina", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/HumanCellAtlas/skylab/HCA_SmartSeq2",
                                                                      version_id="dockstore",
                                                                      relative_path="../../test/smartseq2_single_sample/pr/dockstore_test_inputs.json",
                                                                      platform="Cromwell",
                                                                      metadata="HCA via CZI", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="CWL",
                                                                      id="#workflow/github.com/DataBiosphere/topmed-workflows/TOPMed_alignment_pipeline_CWL",
                                                                      version_id="1.31.0",
                                                                      relative_path="topmed-alignment.sample.json",
                                                                      platform="Arvados",
                                                                      metadata="AGHA via Veritas", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/DataBiosphere/topmed-workflows/u_of_Michigan_alignment_pipeline",
                                                                      version_id="1.29.0",
                                                                      relative_path="u_of_michigan_aligner.json",
                                                                      platform="Cromwell",
                                                                      metadata="HCA via CZI", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/DataBiosphere/topmed-workflows/u_of_Michigan_alignment_pipeline",
                                                                      version_id="1.29.0",
                                                                      relative_path="u_of_michigan_aligner.json",
                                                                      platform="Cromwell",
                                                                      metadata="TOPMed, HCA via Broad", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/DataBiosphere/topmed-workflows/u_of_Michigan_alignment_pipeline",
                                                                      version_id="1.29.0",
                                                                      relative_path="u_of_michigan_aligner.json",
                                                                      platform="Cromwell",
                                                                      metadata="GEL, AGHA via Illumina", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/DataBiosphere/topmed-workflows/u_of_Michigan_alignment_pipeline",
                                                                      version_id="1.31.0",
                                                                      relative_path="u_of_michigan_aligner.json",
                                                                      platform="Cromwell",
                                                                      metadata="HCA via CZI", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/DataBiosphere/topmed-workflows/TopMed_Variant_Caller",
                                                                      version_id="1.29.0",
                                                                      relative_path="topmed_freeze3_calling.json",
                                                                      platform="Cromwell",
                                                                      metadata="TOPMed, HCA via Broad", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="WDL",
                                                                      id="#workflow/github.com/DataBiosphere/topmed-workflows/TopMed_Variant_Caller",
                                                                      version_id="1.29.0",
                                                                      relative_path="topmed_freeze3_calling.json",
                                                                      platform="Cromwell",
                                                                      metadata="GEL, AGHA via Illumina", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="CWL",
                                                                      id="quay.io/pancancer/pcawg-bwa-mem-workflow",
                                                                      version_id="checker",
                                                                      relative_path="Dockstore_cwl.json",
                                                                      platform="Arvados",
                                                                      metadata="AGHA via Veritas", verified=True).response().result
print response
response = client.extendedGA4GH.toolsIdVersionsVersionIdTypeTestsPost(type="CWL",
                                                                      id="#workflow/github.com/bcbio/bcbio_validation_workflows/wes-agha-test-arvados",
                                                                      version_id="master",
                                                                      relative_path="main-wes_chr21_test-samples.json",
                                                                      platform="Arvados",
                                                                      metadata="AGHA via Veritas", verified=True).response().result
print response
