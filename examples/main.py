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

"""Bind the App Engine service endpoints."""

__author__ = 'John Orr (jorr@google.com)'

import webapp2

# The following import is needed in order to add third-party libraries
# before loading any other modules.
import appengine_config  # pylint: disable-msg=unused-import

import handlers


app = webapp2.WSGIApplication([
    (r'/handler/([0-9a-fA-F]+)/(.*)/', handlers.XBlockEndpointHandler),
    (r'/local_resource/([^/]*)/(.*)', handlers.XBlockLocalResourceHandler),
    (r'/display_xblock', handlers.DisplayXblockPageHandler),
    (r'/rest/xblock', handlers.XblockRestHandler),
    (r'/rest/xblock/([0-9a-fA-F]+)', handlers.XblockRestHandler),
    (r'/.*', handlers.DefaultPageHandler)
], debug=True)
