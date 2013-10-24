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

"""Datastore classes for using XBlocks with Google App Engine."""

__author__ = 'John Orr (jorr@google.com)'

import json
from xblock.fields import Scope
import xblock.runtime

from google.appengine.ext import ndb


class DefinitionEntity(ndb.Model):
    block_type = ndb.StringProperty(indexed=False)


class UsageEntity(ndb.Model):
    definition = ndb.KeyProperty(kind=DefinitionEntity, indexed=False)


class KeyValueEntity(ndb.Model):
    value_json = ndb.TextProperty(indexed=False)


class UsageStore(xblock.runtime.UsageStore):
    """Implementation of XBlock UsageStore using App Engine datastore.

    The usage store manages the graph of many-to-one relationships between
    usages, definitions, and blocks. The schema is:
        usage (n) -- (1) definition (n) -- (1) block_type
    """

    def create_usage(self, def_id):
        """Create a new usage id bound to the given definition id."""
        definition = ndb.Key(DefinitionEntity, int(def_id))
        assert definition.get() is not None
        usage = UsageEntity(definition=definition)
        key = usage.put()
        return str(key.id())

    def get_definition_id(self, usage_id):
        """Retrieve the definition id to which this usage id is bound."""
        usage = ndb.Key(UsageEntity, int(usage_id)).get()
        return str(usage.definition.id())

    def create_definition(self, block_type):
        """Create a new definition id, bound to the given block type.

        Args:
            block_type: str. The type of the XBlock for this definition.

        Returns:
            str. The id of the new definition.
        """
        definition = DefinitionEntity(block_type=block_type)
        key = definition.put()
        return str(key.id())

    def get_block_type(self, def_id):
        """Retrieve the block type to which this definition is bound."""
        definition = ndb.Key(DefinitionEntity, int(def_id)).get()
        return definition.block_type


class KeyValueStore(xblock.runtime.KeyValueStore):
    """Implementation of XBlock KeyValueStore using App Engine datastore."""

    def _key_string(self, key):
        key_list = []
        if key.scope == Scope.children:
            key_list.append('children')
        elif key.scope == Scope.parent:
            key_list.append('parent')
        else:
            key_list.append(
                ['usage', 'definition', 'type', 'all'][key.scope.block])

        if key.block_scope_id is not None:
            key_list.append(key.block_scope_id)
        if key.user_id:
            key_list.append(key.user_id)
        key_list.append(key.field_name)
        return '.'.join(key_list)

    def get(self, key):
        """Retrieve the value for the given key.

        Args:
            key: xblock.runtime.KeyValueStore.Key. The key being retrieved.

        Returns:
            The value stored in the datastore under this key.

        Raises:
            KeyError: If there is no matching key in the store.
        """
        kv_entity = ndb.Key(KeyValueEntity, self._key_string(key)).get()
        if kv_entity is None:
            raise KeyError()
        return json.loads(kv_entity.value_json)['value']

    def set(self, key, value):
        """Sets the given value in the store. Overwrite any previous value."""
        key = ndb.Key(KeyValueEntity, self._key_string(key))
        KeyValueEntity(key=key, value_json=json.dumps({'value': value})).put()

    def delete(self, key):
        """Deletes the given key from the store. No-op if the key is absent."""
        ndb.Key(KeyValueEntity, self._key_string(key)).delete()

    def has(self, key):
        """Checks whether the key already has a value set in the store."""
        return ndb.Key(KeyValueEntity, self._key_string(key)).get() is not None
