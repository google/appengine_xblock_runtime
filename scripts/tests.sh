#! /bin/bash
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# author: jorr@google.com (John Orr)
#
# This script runs the test suite.
#

. scripts/common.sh

export PYTHONPATH=$GOOGLE_APP_ENGINE_HOME:$GOOGLE_APP_ENGINE_HOME/lib/webob-1.2.3:examples/lib/XBlock

python -m unittest discover -v -s ./tests
