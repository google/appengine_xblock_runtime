#! /bin/bash
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# author: jorr@google.com (John Orr)
#
# This script starts the sample XBlock demo on the local development server.
#

. scripts/common.sh

cd examples
$GOOGLE_APP_ENGINE_HOME/dev_appserver.py $* .
