#!/usr/bin/env/python

import sys
import pkg_resources
import argparse
import synorchestrator


def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser(
        description='Synapse Workflow Orchestrator'
    )

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--version", action="store_true", default=False)

    args = parser.parse_args(argv)

    if args.version:
        pkg = pkg_resources.require('synapse-orchestrator')
        print u"%s %s" % (sys.argv[0], pkg[0].version)
        exit(0)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
