#!/usr/bin/env python

import sys
import argparse
import pkg_resources  # part of setuptools
import logging
from synorchestrator.orchestrator import monitor

logging.basicConfig(level=logging.INFO)


def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser(description='Synapse Workflow Orchestrator')
    parser.add_argument("--version", action="store_true", default=False)
    args = parser.parse_args(argv)

    if args.version:
        pkg = pkg_resources.require('synapse-orchestrator')
        print(u"%s %s" % (sys.argv[0], pkg[0].version))
        exit(0)

    monitor()


if __name__ == '__main__':
    main(sys.argv[1:])
