import os
import schema_salad.ref_resolver
import urllib
from wes_service.util import visit

def _fixpaths(basedir):
    """
    Adapted from @teton's function in
    https://github.com/common-workflow-language/workflow-service/
    blob/master/wes_client/__init__.py
    """
    def _pathfixer(d):
        if isinstance(d, dict):
            if "path" in d:
                if ":" not in d["path"]:
                    local_path = os.path.normpath(
                        os.path.join(os.getcwd(), basedir, d["path"]))
                    d["location"] = urllib.pathname2url(local_path)
                else:
                    d["location"] = d["path"]
                del d["path"]
            if d.get("class") == "Directory":
                loc = d.get("location", "")
                if loc.startswith("http:") or loc.startswith("https:"):
                    logging.error("Directory inputs not supported with"
                                  " http references")
                    exit(33)
    return _pathfixer


def params_url2object(params_url):
    """
    Resolve references and return object corresponding to the
    JSON params file at the specified URL.

    Adapted from @teton's function in
    https://github.com/common-workflow-language/workflow-service/
    blob/master/wes_client/__init__.py
    """
    loader = schema_salad.ref_resolver.Loader({
        "location": {"@type": "@id"},
        "path": {"@type": "@id"}
    })
    params_object, _ = loader.resolve_ref(params_url)
    basedir = os.path.dirname(params_url)
    params_fixpaths = _fixpaths(basedir)
    visit(params_object, params_fixpaths)

    return params_object


def build_trs_request():
    """
    Prepare Tool Registry Service request for a given submission.
    """
    pass

def build_wes_request(
    workflow_params, workflow_descriptor=None, workflow_url=None,
    workflow_type='CWL', workflow_version='v1.0'
):
    """
    Prepare Workflow Execution Service request for a given submission.
    """
    if isinstance(workflow_params, basestring):
        workflow_params = params_url2object(workflow_params)
    request = {
        "workflow_descriptor": workflow_descriptor,
        "workflow_url": workflow_url,
        "workflow_params": workflow_params,
        "workflow_type": workflow_type,
        "workflow_type_version": workflow_version
    }
    return {k: v for k, v in request.items()
            if v is not None}
