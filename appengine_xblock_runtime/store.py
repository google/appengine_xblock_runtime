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


class BaseEntity(ndb.Model):
    """The base datastore entity for XBlock data.

    XBlock data is stored in subclasses of this class. The data is wrapped
    as a JSON blob held in the field 'data'. Subclasses provide convenience
    accessor methods.
    """
    data = ndb.TextProperty(indexed=False)

    def _get(self, field_name):
        return json.loads(self.data).get(field_name)

    def _set(self, field_name, value):
        json_dict = json.loads(self.data) if self.data else {}
        json_dict[field_name] = value
        self.data = json.dumps(json_dict)


class DefinitionEntity(BaseEntity):

    @property
    def block_type(self):
        return self._get('block_type')

    @block_type.setter
    def block_type(self, value):
        self._set('block_type', value)


class UsageEntity(BaseEntity):

    @property
    def definition_id(self):
        return self._get('definition_id')

    @definition_id.setter
    def definition_id(self, value):
        self._set('definition_id', value)


class KeyValueEntity(BaseEntity):

    @property
    def value(self):
        return self._get('value')

    @value.setter
    def value(self, value):
        self._set('value', value)


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
        return kv_entity.value

    def set(self, key, value):
        """Sets the given value in the store. Overwrite any previous value."""
        key = ndb.Key(KeyValueEntity, self._key_string(key))
        kv_entity = KeyValueEntity(key=key)
        kv_entity.value = value
        kv_entity.put()

    def delete(self, key):
        """Deletes the given key from the store. No-op if the key is absent."""
        ndb.Key(KeyValueEntity, self._key_string(key)).delete()

    def has(self, key):
        """Checks whether the key already has a value set in the store."""
        return ndb.Key(KeyValueEntity, self._key_string(key)).get() is not None
