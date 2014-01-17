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

from google.appengine.ext import ndb


class IdReader(xblock.runtime.IdReader):
    """Implementation of XBlock IdReader using App Engine datastore."""

    def get_definition_id(self, usage_id):
        """Retrieve the definition id to which this usage id is bound."""
        usage = ndb.Key(store.UsageEntity, int(usage_id)).get()
        return str(usage.definition_id)

    def get_block_type(self, def_id):
        """Retrieve the block type to which this definition is bound."""
        definition = ndb.Key(store.DefinitionEntity, int(def_id)).get()
        return definition.block_type


class IdGenerator(xblock.runtime.IdGenerator):
    """Implementation of XBlock IdGenerator using App Engine datastore.

    This manages the graph of many-to-one relationships between
    usages, definitions, and blocks. The schema is:
        usage (n) -- (1) definition (n) -- (1) block_type
    """

    def create_usage(self, def_id):
        """Create a new usage id bound to the given definition id."""
        definition = ndb.Key(store.DefinitionEntity, int(def_id))
        assert definition.get() is not None
        usage = store.UsageEntity()
        usage.definition_id = def_id
        key = usage.put()
        return str(key.id())

    def create_definition(self, block_type):
        """Create a new definition id, bound to the given block type.

        Args:
            block_type: str. The type of the XBlock for this definition.

        Returns:
            str. The id of the new definition.
        """
        definition = store.DefinitionEntity()
        definition.block_type = block_type
        key = definition.put()
        return str(key.id())


class Runtime(xblock.runtime.Runtime):
    """An XBlock runtime which uses the App Engine datastore."""

    def __init__(self, field_data=None, student_id=None, **kwargs):
        super(Runtime, self).__init__(
            IdReader(),
            field_data or xblock.runtime.KvsFieldData(store.KeyValueStore()),
            **kwargs)
        self.user_id = student_id
