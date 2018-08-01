import os
import urllib
import json
import yaml
import subprocess32
import logging
import schema_salad.ref_resolver
import datetime as dt
from synorchestrator import wdl_parser
from six import itervalues
from past.builtins import basestring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def visit(d, op):
    """Recursively call op(d) for all list subelements and dictionary 'values' that d may have."""
    op(d)
    if isinstance(d, list):
        for i in d:
            visit(i, op)
    elif isinstance(d, dict):
        for i in itervalues(d):
            visit(i, op)


def heredoc(s, inputs_dict):
    import textwrap
    s = textwrap.dedent(s).format(**inputs_dict)
    return s[1:] if s.startswith('\n') else s


def get_yaml(filepath):
    try:
        with open(filepath, 'r') as f:
            return yaml.load(f)
    except IOError:
        logger.exception("No file found.  Please create: %s." % filepath)


def save_yaml(filepath, app_config):
    with open(filepath, 'w') as f:
        yaml.dump(app_config, f, default_flow_style=False)


def get_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except IOError:
        logger.exception("No file found.  Please create: %s." % filepath)


def save_json(filepath, app_config):
    with open(filepath, 'w') as f:
        json.dump(app_config, f, default_flow_style=False)


def ctime2datetime(time_str):
    return dt.datetime.strptime(time_str, '%a %b %d %H:%M:%S %Y')


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds  # noqa
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return '{}h:{}m:{}s'.format(hours, minutes, seconds)


def _fixpaths(basedir):
    """
    Adapted from @tetron's function in
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


def _squash_url_dups(path):
    """
    Remove duplicate 'words' from a URL path.
    """
    path_split = path.split('/')
    path_parts = []
    [path_parts.append(part) for part in path_split
     if part not in path_parts]
    return '/'.join(path_parts)


def params_url2object(params_url, file_params=None):
    """
    Resolve references and return object corresponding to the
    JSON params file at the specified URL.

    Adapted from @tetron's function in
    https://github.com/common-workflow-language/workflow-service/
    blob/master/wes_client/__init__.py
    """
    resolve_keys = {
        "path": {"@type": "@id"},
        'location': {"@type": "@id"}
    }
    if file_params is not None:
        res = urllib.urlopen(_squash_url_dups(params_url))
        params_json = json.loads(res.read())
        for k, v in params_json.items():
            if k in file_params and ':' not in v[0] and ':' not in v:
                resolve_keys[k] = {"@type": "@id"}
    loader = schema_salad.ref_resolver.Loader(resolve_keys)
    params_object, _ = loader.resolve_ref(_squash_url_dups(params_url))
    basedir = os.path.dirname(params_url)
    params_fixpaths = _fixpaths(basedir)
    visit(params_object, params_fixpaths)

    return params_object


def find_asts(ast_root, name):
        """
        Finds an AST node with the given name and the entire subtree under it.
        A function borrowed from scottfrazer.  Thank you Scott Frazer!

        :param ast_root: The WDL AST.  The whole thing generally, but really
                         any portion that you wish to search.
        :param name: The name of the subtree you're looking for, like "Task".
        :return: nodes representing the AST subtrees matching the "name" given.
        """
        nodes = []
        if isinstance(ast_root, wdl_parser.AstList):
            for node in ast_root:
                nodes.extend(find_asts(node, name))
        elif isinstance(ast_root, wdl_parser.Ast):
            if ast_root.name == name:
                nodes.append(ast_root)
            for attr_name, attr in ast_root.attributes.items():
                nodes.extend(find_asts(attr, name))
        return nodes


def get_wdl_inputs(wdl):
    """
    Return inputs specified in WDL descriptor, grouped by type.
    """
    wdl_ast = wdl_parser.parse(wdl.encode('utf-8')).ast()
    workflow = find_asts(wdl_ast, 'Workflow')[0]
    workflow_name = workflow.attr('name').source_string
    decs = find_asts(workflow, 'Declaration')
    wdl_inputs = {}
    for dec in decs:
        if isinstance(dec.attr('type'), wdl_parser.Ast) and 'name' in dec.attr('type').attributes:
            # dec_type = dec.attr('type').attr('name').source_string
            dec_subtype = dec.attr('type').attr('subtype')[0].source_string
            dec_name = '{}.{}'.format(workflow_name,
                                      dec.attr('name').source_string)
            wdl_inputs.setdefault(dec_subtype, []).append(dec_name)
        elif hasattr(dec.attr('type'), 'source_string'):
            dec_type = dec.attr('type').source_string
            dec_name = '{}.{}'.format(workflow_name,
                                      dec.attr('name').source_string)
            wdl_inputs.setdefault(dec_type, []).append(dec_name)
    return wdl_inputs


def get_packed_cwl(workflow_url):
    """
    Create 'packed' version of CWL workflow descriptor.
    """
    return subprocess32.check_output(['cwltool', '--pack', workflow_url])


def sniff_workflow_type_version(descriptor, workflow_type):
    """
    Inspect workflow descriptor contents to check CWL/WDL version.
    """
    if workflow_type == 'CWL':
        return yaml.load(descriptor)['cwlVersion']
    elif workflow_type == 'WDL':
        try:
            return [l.lstrip('version ') for l in descriptor.splitlines() if 'version' in l.split(' ')][0]
        except IndexError:
            return 'draft-2'
    else:
        raise ValueError('Unknown/supported workflow type: %s' % workflow_type)


def build_trs_request():
    """
    Prepare Tool Registry Service request for a given submission.
    """
    pass


def build_wes_request(workflow_params,
                      workflow_descriptor=None,
                      workflow_url=None,
                      workflow_type='CWL',
                      workflow_version=None):
    """
    Prepare Workflow Execution Service request for a given submission.
    """
    if workflow_type == 'WDL':
        tmp_descriptor = workflow_descriptor
        if workflow_descriptor is None:
            res = urllib.urlopen(_squash_url_dups(workflow_url))
            workflow_descriptor = res.read()
        file_params = get_wdl_inputs(workflow_descriptor)['File']
        workflow_descriptor = tmp_descriptor
    else:
        file_params = None

    if isinstance(workflow_params, basestring):
        workflow_params = params_url2object(
            workflow_params, file_params
        )

    if workflow_version is None:
        workflow_version = sniff_workflow_type_version(
            workflow_descriptor, workflow_type
        )

    request = {
        "workflow_descriptor": workflow_descriptor,
        "workflow_url": workflow_url,
        "workflow_params": workflow_params,
        "workflow_type": workflow_type,
        "workflow_type_version": workflow_version
    }
    return {k: v for k, v in request.items()
            if v is not None}
