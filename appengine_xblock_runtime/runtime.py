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

"""Runtime resources for using XBlocks on Google App Engine."""

__author__ = 'John Orr (jorr@google.com)'

from xblock.fields import ScopeIds
import xblock.runtime
import store


class Runtime(xblock.runtime.Runtime):
    """An XBlock runtime which uses the App Engine datastore."""

    def __init__(self, student_id=None):
        super(Runtime, self).__init__(
            store.UsageStore(), xblock.runtime.DbModel(store.KeyValueStore()))
        self.student_id = student_id

    def get_block(self, usage_id):
        """Create an XBlock instance in this runtime."""

        def_id = self.usage_store.get_definition_id(usage_id)
        block_type = self.usage_store.get_block_type(def_id)
        keys = ScopeIds(self.student_id, block_type, def_id, usage_id)
        block = self.construct_xblock(block_type, keys)
        return block
