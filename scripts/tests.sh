#! /bin/bash
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# author: jorr@google.com (John Orr)
#
# This script runs the test suite.
#

. scripts/common.sh

PYTHONPATH=$GOOGLE_APP_ENGINE_HOME
PYTHONPATH=$PYTHONPATH:$GOOGLE_APP_ENGINE_HOME/lib/webob-1.2.3
PYTHONPATH=$PYTHONPATH:examples/lib/XBlock
PYTHONPATH=$PYTHONPATH:examples/lib/XBlock/demo_xblocks
export PYTHONPATH

python -m unittest discover -v -s ./tests
