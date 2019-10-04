#!/bin/bash

cd $TRAVIS_BUILD_DIR/simple
FLASK_RUN_PORT=8050 FLASK_APP=orchestrator.py python -m flask run
