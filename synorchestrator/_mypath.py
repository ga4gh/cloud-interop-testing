import os
import sys

# temp solution to update local Python path
# TODO: create setup.py to build library
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR,"."))
