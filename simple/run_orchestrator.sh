#!/bin/bash

cd $TRAVIS_BUILD_DIR/simple
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=8050
export FLASK_APP=orchestrator.py 
python -m flask run
