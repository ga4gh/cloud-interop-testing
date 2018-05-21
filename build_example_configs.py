import os
import sys
import yaml


def main(argv):
    with open('exampleConfigs.yml', 'rb') as f:
        ex_configs = yaml.load(f)

    for config, opts in ex_configs.items():
        config_path = os.path.expanduser(opts.pop('file'))
        print("saving {} config to {}...".format(config, config_path))
        with open(config_path, 'wb') as f:
            yaml.dump(opts, f, default_flow_style=False)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
