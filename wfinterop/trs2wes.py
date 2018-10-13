#!/usr/bin/env python
"""
For a workflow registered in a given TRS implementation (e.g., 
Dockstore), retrieve details and prepare the workflow run request.
Optionally, retrieve, format, or attach (as a file) workflow 
descriptors, parameters, and inputs to include with request.
"""
import logging
import os
import yaml
import urllib
import json
import re
import glob
import subprocess32

import schema_salad.ref_resolver

from urllib import urlopen
from StringIO import StringIO
from toil.wdl import wdl_parser
from wes_service.util import visit

from wfinterop.config import queue_config
from wfinterop.config import set_yaml
from wfinterop.trs import TRS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def fetch_queue_workflow(queue_id):
    """
    Collect details for the workflow associated with a queue from the
    specified TRS repository.

    Args:
        queue_id (str): string identifying the workflow queue
    
    Returns:
        dict: dict with updated configuration for the workflow queue
    """
    wf_config = queue_config()[queue_id]
    logger.info("Retrieving details for workflow '{}' (queue: '{}')"
                .format(wf_config['workflow_id'], queue_id))
    trs_instance = TRS(wf_config['trs_id'])
    wf_descriptor = trs_instance.get_workflow_descriptor(
        id=wf_config['workflow_id'],
        version_id=wf_config['version_id'],
        type=wf_config['workflow_type']
    )
    wf_files = trs_instance.get_workflow_files(
        id=wf_config['workflow_id'],
        version_id=wf_config['version_id'],
        type=wf_config['workflow_type']
    )
    wf_config['workflow_url'] = wf_descriptor['url']
    attachment_paths = [wf_file['path'] for wf_file in wf_files
                        if wf_file['file_type'] == 'SECONDARY_DESCRIPTOR']
    wf_attachments = []
    for attachment in attachment_paths:
        attachment_file = trs_instance.get_workflow_descriptor_relative(
            id=wf_config['workflow_id'],
            version_id=wf_config['version_id'],
            type=wf_config['workflow_type'],
            relative_path=attachment
        )
        wf_attachments.append(attachment_file['url'])
    wf_config['workflow_attachments'] = wf_attachments
    logger.debug("Found the following data for workflow '{}':\n{}"
                 .format(wf_config['workflow_id'], wf_attachments))
    set_yaml('queues', queue_id, wf_config)
    return wf_config


def store_verification(queue_id, wes_id):
    """
    Record checker status for selected workflow and environment.

    Args:
        queue_id (str): string identifying the workflow queue
    """
    wf_config = queue_config()[queue_id]
    wf_config.setdefault('wes_verified', []).append(wes_id)
    set_yaml('queues', queue_id, wf_config)


# def post_verification(self, id, version_id, type, relative_path, requests):
#     """
#     Annotate test JSON with information on whether it ran successfully on
#     particular platforms plus metadata.
#     """
#     id = _format_workflow_id(id)
#     endpoint ='extended/{}/versions/{}/{}/tests/{}'.format(
#         id, version_id, type, relative_path
#     )
#     return _post_to_endpoint(self, endpoint, requests)


def get_version(extension, workflow_file):
    """
    Determines the version of a .py, .wdl, or .cwl file.

    Args:
        extension (str): string with extension of workflow file
        workflow_file (str): filepath or filename of workflow file

    Returns:
        str: string indicating workflow type version
    """
    if extension == 'cwl':
        return yaml.load(open(workflow_file))['cwlVersion']
    else:  
        # Must be a wdl file.
        # Borrowed from https://github.com/Sage-Bionetworks/synapse-orchestrator/blob/develop/synorchestrator/util.py#L142
        try:
            return [l.lstrip('version') for l in workflow_file.splitlines() 
                    if 'version' in l.split(' ')][0]
        except IndexError:
            return 'draft-2'


def get_wf_info(workflow_path):
    """
    Returns the version of the file and the file extension.

    Assumes that the file path is to the file directly - i.e., ends 
    with a valid file extension. Supports checking local files as well
    as files at http:// and https:// locations. Files at these remote
    locations are recreated locally to enable our approach to version
    checking, then removed after version is extracted.

    Args:
        workflow_path (str): filepath or URL for main workflow
            descriptor file
    
    Returns:
        tuple: tuple containing:

            str: string indicating workflow type version
            str: string indicating workflow type (e.g., 'CWL', 'WDL')
    """
    supported_formats = ['py', 'wdl', 'cwl']
    # Grab the file extension
    file_type = workflow_path.lower().split('.')[-1]  
    workflow_path = (workflow_path if ':' in workflow_path 
                     else 'file://' + workflow_path)

    if file_type in supported_formats:
        if workflow_path.startswith('file://'):
            version = get_version(file_type, workflow_path[7:])
        elif (workflow_path.startswith('https://') or 
              workflow_path.startswith('http://')):
            # If file not local go fetch it.
            html = urlopen(workflow_path).read()
            local_loc = os.path.join(os.getcwd(), 
                                     'fetchedFromRemote.' + file_type)
            with open(local_loc, 'w') as f:
                f.write(html)
            # Don't take the file_type here, found it above.
            version = get_wf_info('file://' + local_loc)[0]  
            # TODO: Find a way to avoid recreating file before version 
            # determination.
            os.remove(local_loc)  
        else:
            raise NotImplementedError("Unsupported workflow file location: "
                                      "{}. Must be local or HTTP(S)."
                                      .format(workflow_path))
    else:
        raise TypeError("Unsupported workflow type: "
                        ".{}. Must be {}."
                        .format(file_type, supported_formats))
    return version, file_type.upper()


def get_packed_cwl(workflow_url):
    """
    Create 'packed' version of CWL workflow descriptor.

    Args:
        workflow_url (str): URL for main workflow descriptor file
    
    Returns:
        str: string with main and all secondary workflow descriptors
            combined CWL workflow
    """
    logger.debug("Packing descriptors for '{}'".format(workflow_url))
    return subprocess32.check_output(['cwltool', '--pack', workflow_url])


def get_flattened_descriptor(workflow_file):
    wf_lines = urlopen(workflow_file).readlines()
    import_lines = [line_num for line_num, line in enumerate(wf_lines) 
                    if 'import' in line]
    for l in import_lines:
        match = re.search('http.*(?=")', wf_lines[l])
        if match is not None:
            path = match.group()
            filename = os.path.basename(path)
            wf_lines[l] = re.sub(path, filename, wf_lines[l]) 
    return ''.join(wf_lines)


def find_asts(ast_root, name):
        """
        Finds an AST node with the given name and the entire subtree
        under it. Function borrowed from scottfrazer.

        Args:
            ast_root: the WDL AST; the whole thing generally, but 
                really any portion that you wish to search
            name (str): the name of the subtree you're looking for,
                like 'Task'
        
        Returns:
            list: nodes representing the AST subtrees matching the
            'name' given
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

    Args:
        wdl (str): string containing the WDL descriptor
    
    Returns:
        dict: dict containing identified workflow inputs, classified
            and grouped by type (e.g., 'File')
    """
    wdl_ast = wdl_parser.parse(wdl.encode('utf-8')).ast()
    workflow = find_asts(wdl_ast, 'Workflow')[0]
    workflow_name = workflow.attr('name').source_string
    decs = find_asts(workflow, 'Declaration')
    wdl_inputs = {}
    for dec in decs:
        if (isinstance(dec.attr('type'), wdl_parser.Ast) and 
            'name' in dec.attr('type').attributes):
            dec_type = dec.attr('type').attr('name').source_string
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


def modify_jsonyaml_paths(jsonyaml_file, path_keys=None):
    """
    Changes relative paths in a json/yaml file to be relative to where
    the JSON/YAML file is located.

    Args:
        jsonyaml_file (str): filepath or URL for JSON/YAML file
            containing workflow parameters
        path_keys (:obj:`list` of :obj:`str`): list of workflow
            parameter names to modify

    Returns:
        str: string contents of JSON/YAML file with modified paths
    """
    logger.debug("Resolving paths in parameters file '{}'"
                 .format(jsonyaml_file))
    resolve_keys = {
        "path": {"@type": "@id"},
        'location': {"@type": "@id"}
    }
    if path_keys is not None:
        res = urllib.urlopen(jsonyaml_file)
        params_json = json.loads(res.read())
        for k, v in params_json.items():
            if k in path_keys and not ':' in v[0] and not ':' in v:
                resolve_keys[k] = {"@type": "@id"}
    loader = schema_salad.ref_resolver.Loader(resolve_keys)
    input_dict, _ = loader.resolve_ref(jsonyaml_file, checklinks=False)
    basedir = os.path.dirname(jsonyaml_file)

    def fixpaths(d):
        """Make sure all paths have a URI scheme."""
        if isinstance(d, dict):
            if "path" in d:
                if ":" not in d["path"]:
                    local_path = os.path.normpath(os.path.join(os.getcwd(), basedir, d["path"]))
                    d["location"] = urllib.pathname2url(local_path)
                else:
                    d["location"] = d["path"]
                del d["path"]

    visit(input_dict, fixpaths)
    return json.dumps(input_dict)


def get_wf_descriptor(workflow_file, 
                      parts=None, 
                      attach_descriptor=False,
                      pack_descriptor=False):
    """
    Retrieve descriptor URL or contents for the workflow.

    Args:
        workflow_file (str): ...
        parts (:obj:`list` of :obj:`tuple`): ...
        attach_descriptor (bool): ...
        pack_descriptor (bool): ...
    """
    if parts is None:
        parts = []

    if workflow_file.startswith("file://"):
        parts.append(
            ("workflow_attachment", 
                (os.path.basename(workflow_file[7:]), 
                 open(workflow_file[7:], "rb"))
            )
        )
        parts.append(
            ("workflow_url", os.path.basename(workflow_file[7:]))
        )
    elif workflow_file.startswith("http") and attach_descriptor:
        if pack_descriptor:
            descriptor_f = StringIO(get_packed_cwl(workflow_file))
        else:
            descriptor_f = urlopen(workflow_file).read()
        parts.append(
            ("workflow_attachment", 
                (os.path.basename(workflow_file), descriptor_f)
            )
        )
        parts.append(
            ("workflow_url", os.path.basename(workflow_file))
        )
    else:
        parts.append(("workflow_url", workflow_file))

    return parts


def get_wf_inputs(workflow_file, wf_params, parts=None):
    """
    Download and attach input files listed in the workflow 
    parameters. Only files hosted in public GitHub repositories
    are currently supported for attaching.

    Args:
        workflow_file (str): ...
        wf_params (str): ...
        parts (:obj:`list` of :obj:`tuple`): ...
    """
    if parts is None:
        parts = []
    wf_params = json.loads(wf_params)
    base_path = os.path.dirname(workflow_file)
    for param in wf_params.values():
        if isinstance(param, str) or isinstance(param, unicode):
            if param.startswith('https://raw.githubusercontent.com'):
                attach_f = urlopen(param)
                parts.append(("workflow_attachment", 
                        (re.sub(base_path + '/', '', param), attach_f)))
                return parts
        elif isinstance(param, dict):
            return get_wf_inputs(workflow_file, 
                                 wf_params=json.dumps({'url': param['location']}),
                                 parts=parts)


def get_wf_params(workflow_file, 
                  workflow_type, 
                  jsonyaml, 
                  parts=None, 
                  fix_paths=False,
                  attach_inputs=False):
    """
    Retrieve and format workflow parameters for execution.

    Args:
        workflow_file (str): ...
        workflow_type (str): ...
        jsonyaml (str): ...
        parts (:obj:`list` of :obj:`tuple`): ...
        fix_paths (bool): ...
        attach_inputs (bool): ...
    """
    if parts is None:
        parts = []

    if jsonyaml.startswith("file://"):
        jsonyaml = jsonyaml[7:]
        with open(jsonyaml) as f:
            wf_params = json.dumps(json.load(f))
    elif jsonyaml.startswith("http"):
        if fix_paths:
            input_keys = None
            if workflow_type == 'WDL':
                res = urllib.urlopen(workflow_file)
                workflow_descriptor = res.read()
                input_keys = get_wdl_inputs(workflow_descriptor)['File']
            wf_params_fixed = modify_jsonyaml_paths(jsonyaml, 
                                                    path_keys=input_keys)
            if attach_inputs:
                parts = get_wf_inputs(workflow_file, wf_params_fixed, parts)
                wf_params = json.dumps(json.loads(urllib.urlopen(jsonyaml).read()))
            else:
                wf_params = wf_params_fixed
        else:
            wf_params = json.dumps(json.loads(urllib.urlopen(jsonyaml).read()))
    else:
        with open(jsonyaml) as f:
            wf_params = json.dumps(json.load(f))

    parts.append(("workflow_params", wf_params))
    return parts
    

def get_wf_attachments(workflow_file, attachments, parts=None):
    """
    Retrieve and attach any additional files needed to run 
    the workflow. Attachments should nominally be hosted in the
    same remote repository as the primary workflow descriptor
    and specified using the full URL. Local file attachments
    are supported but discouraged.

    Args:
        workflow_file (str): ...
        attachments (:obj:`list` of :obj:`str`): ...
        parts (:obj:`list` of :obj:`tuple`): ...
    """
    if parts is None:
        parts = []

    base_path = os.path.dirname(workflow_file)
    for attachment in attachments:
        if attachment.startswith("file://"):
            attachment = attachment[7:]
            attach_f = open(attachment, "rb")
        elif attachment.startswith("http"):
            attach_f = urlopen(attachment)

        parts.append(("workflow_attachment", 
                     (re.sub(base_path + '/', '', attachment), attach_f)))
    return parts


def expand_globs(attachments):
    expanded_list = []
    for filepath in attachments:
        if 'file://' in filepath:
            for f in glob.glob(filepath[7:]):
                expanded_list += ['file://' + os.path.abspath(f)]
        elif ':' not in filepath:
            for f in glob.glob(filepath):
                expanded_list += ['file://' + os.path.abspath(f)]
        else:
            expanded_list += [filepath]
    return set(expanded_list)


def build_wes_request(workflow_file,
                      jsonyaml,
                      attachments=None,
                      attach_descriptor=False,
                      pack_descriptor=False,
                      attach_imports=False,
                      resolve_params=False,
                      attach_inputs=False):
    """
    Construct and format Workflow Execution Service POST request to
    create a new workflow run. Named parts (primitive types or files)
    are submitted as 'multipart/form-data'.

    Args:
        workflow_file (str): path to CWL/WDL file; can be 
            http/https/file path or URL
        jsonyaml (str): path to accompanying JSON or YAML file
        attachments (:obj:`list` of :obj:`str`): any other files
            needing to be uploaded to the server
        attach_descriptor (bool): ...
        pack_descriptor (bool): ...
        attach_imports (bool): ...
        resolve_params (bool): ...
        attach_imports (bool): ...
 
    Returns:
        list: list of tuples formatted to be sent in a POST request to
            the WES server (Swagger API)
    """
    workflow_file = "file://" + workflow_file if ":" not in workflow_file else workflow_file
    wf_version, wf_type = get_wf_info(workflow_file)
    
    parts = [("workflow_type", wf_type),
             ("workflow_type_version", wf_version)]

    if pack_descriptor:
        if wf_type == 'WDL':
            logger.debug("Descriptor packing not applicable for WDL "
                         "workflows; imports must be attached or specified "
                         "as full URLs.")
            pack_descriptor = False
        else:
            logger.debug("Packed descriptors much be attached; "
                         "no need to attach imports")
            attach_descriptor = True
            attach_imports = False
    if attach_inputs:
        logger.debug("Attachment only supported for input files hosted "
                     "on GitHub; parameter paths will be resolved to "
                     "full URLs.")
        resolve_params = True
    parts = get_wf_descriptor(workflow_file, 
                              parts, 
                              attach_descriptor,
                              pack_descriptor)
    parts = get_wf_params(workflow_file, 
                          wf_type, 
                          jsonyaml, 
                          parts, 
                          fix_paths=resolve_params,
                          attach_inputs=attach_inputs)

    if not attach_imports:
        ext_re = re.compile('{}$'.format(wf_type.lower()))
        attachments = [attach for attach in attachments
                       if not ext_re.search(attach)]

    if attachments:
        attachments = expand_globs(attachments)
        parts = get_wf_attachments(workflow_file, attachments, parts)

    return parts


