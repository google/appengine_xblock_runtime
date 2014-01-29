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

"""Unit tests for the datastore backed storage classes."""

__author__ = 'John Orr (jorr@google.com)'

import unittest

from appengine_xblock_runtime import store
import appengine_xblock_runtime.runtime
import xblock.exceptions
import xblock.fields
import xblock.runtime
from google.appengine.ext import testbed


class BaseTestCase(unittest.TestCase):
    """Base class for unt tests. Sets up mock datastiore and memcache."""

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()


class TestUsageStore(BaseTestCase):
    """Unit tests for the usage store."""

    def setUp(self):
        super(TestUsageStore, self).setUp()
        self.id_reader = appengine_xblock_runtime.runtime.IdReader()
        self.id_generator = appengine_xblock_runtime.runtime.IdGenerator()

    def test_create_and_get_definition(self):
        '''Should be able to create and then retrieve a definition id.'''
        def_id = self.id_generator.create_definition('my_block')
        self.assertEqual('my_block', self.id_reader.get_block_type(def_id))

    def test_create_and_get_usage(self):
        '''Should be able to create and then retrieve a usage id.'''
        def_id = self.id_generator.create_definition('my_block')
        usage_id = self.id_generator.create_usage(def_id)
        self.assertEqual(def_id, self.id_reader.get_definition_id(usage_id))

    def test_cannot_create_usage_with_nonexistent_definition(self):
        '''Should not create a usage bound to a non-existent definition.'''
        try:
            self.id_generator.create_usage('123')
            self.fail('Expected assertion to fail')
        except AssertionError:
            pass

    def test_get_non_existent_usage_raises_exception(self):
        """Should raise NoSuchUsage when non-existent usage_id requested."""
        try:
            self.id_reader.get_definition_id('i_dont_exist')
            self.fail('Expected NoSuchUsage exception')
        except xblock.exceptions.NoSuchUsage:
            pass

    def test_get_non_existent_definition_raises_exception(self):
        """Should raise NoSuchDefinition when non-existent def_id requested."""
        try:
            self.id_reader.get_block_type('i_dont_exist')
            self.fail('Expected NoSuchDefinition exception')
        except xblock.exceptions.NoSuchDefinition:
            pass


class TestKeyValueStore(BaseTestCase):
    """Unit tests for the key value store."""

    def setUp(self):
        super(TestKeyValueStore, self).setUp()
        self.key_value_store = store.KeyValueStore()

    def _user_state_key(self):
        return xblock.runtime.KeyValueStore.Key(
            scope=xblock.fields.Scope.user_state, user_id='123',
            block_scope_id='456', field_name='my_field')

    def test_set_then_get(self):
        '''Should set and then retrieve string value from KVS.'''
        key = self._user_state_key()
        self.key_value_store.set(key, 'data')
        self.assertTrue(self.key_value_store.has(key))
        self.assertEqual('data', self.key_value_store.get(key))

    def test_set_then_get_rich_data(self):
        '''Should set and then retrieve structured data from KVS.'''
        key = self._user_state_key()
        data = {
            'a': 'A',
            'b': 3.14,
            'c': {
                'aa': 'AA',
                'bb': [1, 2, 3]}}
        self.key_value_store.set(key, data)
        self.assertTrue(self.key_value_store.has(key))
        self.assertEqual(data, self.key_value_store.get(key))

    def test_get_without_set(self):
        '''Attempt to get unset key should raise KeyError.'''
        key = self._user_state_key()
        try:
            self.key_value_store.get(key)
            self.fail('Expected KeyError')
        except KeyError:
            pass

    def test_delete(self):
        '''Should be able to delete existing key from KVS.'''
        key = self._user_state_key()
        self.key_value_store.set(key, 'data')
        self.assertTrue(self.key_value_store.has(key))
        self.assertEqual('data', self.key_value_store.get(key))

        self.key_value_store.delete(key)
        self.assertFalse(self.key_value_store.has(key))
        try:
            self.key_value_store.get(key)
            self.fail('Expected KeyError')
        except KeyError:
            pass

    def test_delete_without_add(self):
        '''Delete of non-existent key should pass as no-op.'''
        key = self._user_state_key()
        self.assertFalse(self.key_value_store.has(key))
        # Expect no exception
        self.key_value_store.delete(key)
        self.assertFalse(self.key_value_store.has(key))

    def test_has_finds_key(self):
        '''Should be able to detect presence of key.'''
        key = self._user_state_key()
        self.key_value_store.set(key, 'data')
        self.assertTrue(self.key_value_store.has(key))

    def test_has_does_not_find_key(self):
        '''Should be able to detect absence of key.'''
        key = self._user_state_key()
        self.assertFalse(self.key_value_store.has(key))
