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

"""Integration tests for the XBlock runtime using the App Engine datastore."""

__author__ = 'John Orr (jorr@google.com)'

import unittest

from appengine_xblock_runtime import runtime
from appengine_xblock_runtime import store
import xblock.fields
import xblock.runtime
from google.appengine.ext import testbed


class RuntimeForTest(runtime.Runtime):

    def handler_url(
            self, block, handler_name, suffix='', query='', thirdparty=False):
        raise Exception("Not Used By Tests")

    def resources_url(self, resource):
        raise Exception("Not Used By Tests")

    def local_resource_url(self, block, uri):
        raise Exception("Not Used By Tests")


class TestRuntime(unittest.TestCase):
    """Integration tests between XBlock and the runtime."""

    STUDENT_ID = 'student_01'

    def setUp(self):
        super(TestRuntime, self).setUp()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.runtime = RuntimeForTest(student_id=self.STUDENT_ID)
        self.id_generator = runtime.IdGenerator()

    def test_html_block(self):
        """Test persistence of fields in content scope."""
        usage_id = self.runtime.parse_xml_string(
            '<html_demo>text</html_demo>', self.id_generator)
        block = self.runtime.get_block(usage_id)

        key = xblock.runtime.KeyValueStore.Key(
            scope=xblock.fields.Scope.content,
            user_id=None,
            block_scope_id=block.scope_ids.def_id,
            field_name='content')

        self.assertEqual('text', store.KeyValueStore().get(key))

    def test_slider_block(self):
        """Test peristence of fields in user scope."""
        usage_id = self.runtime.parse_xml_string(
            '<slider_demo/>', self.id_generator)
        block = self.runtime.get_block(usage_id)

        block.value = 50
        block.save()

        key = xblock.runtime.KeyValueStore.Key(
            scope=xblock.fields.Scope.user_state,
            user_id=self.STUDENT_ID,
            block_scope_id=block.scope_ids.usage_id,
            field_name='value')

        self.assertEqual(50, store.KeyValueStore().get(key))
