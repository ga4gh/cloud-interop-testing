import os
import re
import json
import yaml
import logging
import subprocess32
import datetime as dt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _replace_env_var(match):
    # from https://github.com/zhouxiaoxiang/oriole/blob/master/oriole/yml.py
    env_var, default = match.groups()
    if env_var == 'GCLOUD_TOKEN':
        return subprocess32.check_output(
            ['gcloud', 'auth', 'print-access-token']
            ).rstrip()
    else:
        return os.environ.get(env_var, default)


def _env_var_constructor(loader, node):
    # from https://github.com/zhouxiaoxiang/oriole/blob/master/oriole/yml.py
    var = re.compile(r"\$\{([^}:\s]+):?([^}]+)?\}", re.VERBOSE)
    value = loader.construct_scalar(node)
    return var.sub(_replace_env_var, value)


def setup_yaml_parser():
    # from https://github.com/zhouxiaoxiang/oriole/blob/master/oriole/yml.py
    var = re.compile(r".*\$\{.*\}.*", re.VERBOSE)
    yaml.add_constructor('!env_var', _env_var_constructor)
    yaml.add_implicit_resolver('!env_var', var)


setup_yaml_parser()


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
        json.dump(app_config, f, indent=4)


def response_handler(response):
    try:
        return response.response().result
    except:
        return response


def ctime2datetime(time_str):
    return dt.datetime.strptime(time_str, '%a %b %d %H:%M:%S %Y')


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds  # noqa
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return '{}h:{}m:{}s'.format(hours, minutes, seconds)
