#!/usr/bin/env python
"""
Convenience methods related to handling and manipulating files,
strings, and dates. Methods are used throughout other modules to 
streamline common operations.
"""
import logging
import os
import re
import json
import yaml
import subprocess32

import datetime as dt

from contextlib import contextmanager
from urllib import urlopen
from bson import json_util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def open_file(path, mode):
    if mode.startswith('w'):
        if path.startswith('http'):
            raise ValueError
        else:
            f = open(path, mode)
    else:
        f = urlopen(path)
    yield f
    f.close()


def _replace_env_var(match):
    """
    For a matched environment variable, return the appropriate value
    based on pre-defined mapping.

    Args:
        match (SRE_Match): :class:`SRE_Match` object returned from
            searching a string for environment variables matching pattern
            '${ENV_VAR}' 

    Returns:
        str: string with the value of the matched environment variable
    """
    env_var, default = match.groups()
    if env_var == 'GCLOUD_TOKEN':
        try:
            return subprocess32.check_output(
                ['gcloud', 'auth', 'print-access-token']
            ).rstrip()
        except OSError:
            return '!! gcloud not installed !!'
    else:
        return os.environ.get(env_var, default)


def _env_var_constructor(loader, node):
    """
    Replace a parsed environment variable with the value during YAML
    parsing.
    
    Args:
        loader (Constructor): YAML :class:`Constructor` to use for
            parsing nodes during file loading
        node (Node): The YAML :class:`Node` to parse
    
    Returns:
        str: string with matched environment variable replaced with
            the corresponding value of the environment variable.
    """
    var = re.compile(r"\$\{([^}:\s]+):?([^}]+)?\}", re.VERBOSE)
    value = loader.construct_scalar(node)
    return var.sub(_replace_env_var, value)


def setup_yaml_parser():
    """
    Add environment variable parsing logic to YAML module config.

    This and dependent functions were adopted from
    https://github.com/zhouxiaoxiang/oriole/blob/master/oriole/yml.py
    """
    var = re.compile(r".*\$\{.*\}.*", re.VERBOSE)
    yaml.add_constructor('!env_var', _env_var_constructor)
    yaml.add_implicit_resolver('!env_var', var)


setup_yaml_parser()


def heredoc(s, inputs_dict):
    """
    Use docstrings to specify a multi-line string literal.

    Args:
        s (str): docstring with named placeholders for replacement.
        inputs_dict (dict): dict with keys corresponding to placeholders
            in docstring `s` and values to insert.

    Returns:
        str: string with placeholders replaced with corresponding values
            and any linebreaks preserved.
    """
    import textwrap
    s = textwrap.dedent(s).format(**inputs_dict)
    return s[1:] if s.startswith('\n') else s


def get_yaml(filepath):
    """
    Read YAML data from a file into a dict.

    Args:
        filepath (str): local filepath of the YAML file

    Returns:
        dict: dict with loaded/parsed data from the YAML file
    """
    try:
        with open_file(filepath, 'r') as f:
            return yaml.load(f)
    except IOError:
        logger.exception("No file found.  Please create: %s." % filepath)


def save_yaml(filepath, app_config):
    """
    Write YAML data from a dict to a file.

    Args:
        filepath (str): local filepath of the YAML file
        app_config (dict): dict containing the data to write
    """
    with open_file(filepath, 'w') as f:
        yaml.dump(app_config, f, default_flow_style=False)


def get_json(filepath):
    """
    Read JSON data from a file into a dict.

    Args:
        filepath (str): local filepath of the JSON file

    Returns:
        dict: dict with loaded/parsed data from the JSON file
    """
    try:
        with open_file(filepath, 'r') as f:
            return json.load(f)
    except IOError:
        logger.exception("No file found.  Please create: %s." % filepath)


def save_json(filepath, app_config):
    """
    Write JSON data from a dict to a file.

    Args:
        filepath (str): local filepath of the JSON file
        app_config (dict): dict containing the data to write
    """
    with open_file(filepath, 'w') as f:
        json.dump(app_config, f, indent=4, default=str)


def response_handler(response):
    """
    Parse the response from a REST API request and return object
    in common format.

    Args:
        response: response object from a REST request
    """
    try:
        return response.response().result
    except:
        return response


def ctime2datetime(time_str):
    """
    Parse `ctime()` style string into :class:`datetime` object. 
    
    Args:
        time_str (str): string with date and time information
    
    Returns:
        datetime: :class:`datetime` object
    """
    return dt.datetime.strptime(time_str, '%a %b %d %H:%M:%S %Y')


def convert_timedelta(duration):
    """
    Return time duration as formatted string.

    Args:
        duration (timedelta): :class:`timedelta` object representing
            the difference between two :class:`datetime` objects
    
    Returns:
        str: string representation of the duration
    """
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return '{}h:{}m:{}s'.format(hours, minutes, seconds)
