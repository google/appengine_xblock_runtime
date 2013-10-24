# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Load the XBlock eggs used by the server."""

__author__ = 'John Orr (jorr@google.com)'

import os
import pkg_resources


# this is the official location of this app for computing of all relative paths
BUNDLE_ROOT = os.path.dirname(__file__)

eggs = ['appengine_xblock_runtime', 'XBlock', os.path.join('XBlock', 'thumbs')]
for egg in eggs:
    egg = os.path.join(BUNDLE_ROOT, 'lib', egg)
    pkg_resources.working_set.add_entry(egg)
