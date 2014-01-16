# Copyright 2013 Google Inc. All Rights Reserved.
#
# author: jorr@google.com (John Orr)

CWD=`pwd`

XBLOCK_GIT_REV=40a949eb934ddb7ec71cd6b935772500aec8bf1c

# Locate or install Google App Engine SDK
GOOGLE_APP_ENGINE_HOME=
if [ ! -d "$GOOGLE_APP_ENGINE_HOME" ]; then
  APPCFG=`which appcfg.py`
  if [ -x "$APPCFG" ]; then
    GOOGLE_APP_ENGINE_HOME=`dirname "$APPCFG"`
  elif [ -d google_appengine ]; then
    GOOGLE_APP_ENGINE_HOME="$CWD/google_appengine"
  else
    echo Installing GAE
    wget http://googleappengine.googlecode.com/files/google_appengine_1.8.2.zip -O google_appengine_1.8.2.zip
    unzip google_appengine_1.8.2.zip
    rm google_appengine_1.8.2.zip
    GOOGLE_APP_ENGINE_HOME="$CWD/google_appengine"
  fi
fi

# Install required libraries for the app
mkdir -p examples/lib
cd examples/lib
if [ ! -d appengine_xblock_runtime ]; then
  mkdir appengine_xblock_runtime
  cp -a ../../appengine_xblock_runtime appengine_xblock_runtime
  cp -a ../../setup.py appengine_xblock_runtime
  cd appengine_xblock_runtime
  python setup.py egg_info
  cd ..
fi
if [ ! -d XBlock ]; then
  git clone https://github.com/edx/XBlock.git
  cd XBlock
  git checkout $XBLOCK_GIT_REV
  python setup.py egg_info
  cd thumbs
  python setup.py egg_info
  cd ../demo_xblocks
  python setup.py egg_info
  cd ../..
fi
cd ../..
