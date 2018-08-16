import json
import yaml
import logging
import datetime as dt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def ctime2datetime(time_str):
    return dt.datetime.strptime(time_str, '%a %b %d %H:%M:%S %Y')


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds  # noqa
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return '{}h:{}m:{}s'.format(hours, minutes, seconds)
