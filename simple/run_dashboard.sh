#!/bin/bash

cd $TRAVIS_BUILD_DIR/simple
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=8060
export FLASK_APP=dashboard.py
python -m flask run
