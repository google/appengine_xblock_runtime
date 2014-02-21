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

import logging
import uuid

import store

import xblock.exceptions
import xblock.runtime

from google.appengine.ext import ndb


logging.warning("""
WARNING: This version of the App Engine XBlock Runtime does not implement any
transactional locking. As a result, during periods of high traffic, inconsistent
results are possible arising from race conditions and data contention. We are
actively working on this, and future releases of the runtime will mitigate the
issue.""")


def generate_id():
    return uuid.uuid4().hex


class IdReader(xblock.runtime.IdReader):
    """Implementation of XBlock IdReader using App Engine datastore."""

    def get_definition_id(self, usage_id):
        """Retrieve the definition id to which this usage id is bound."""
        usage = ndb.Key(store.UsageEntity, str(usage_id)).get()
        if usage is None:
            raise xblock.exceptions.NoSuchUsage(str(usage_id))
        return str(usage.definition_id)

    def get_block_type(self, def_id):
        """Retrieve the block type to which this definition is bound."""
        definition = ndb.Key(store.DefinitionEntity, str(def_id)).get()
        if definition is None:
            raise xblock.exceptions.NoSuchDefinition(str(def_id))
        return definition.block_type


class IdGenerator(xblock.runtime.IdGenerator):
    """Implementation of XBlock IdGenerator using App Engine datastore.

    This manages the graph of many-to-one relationships between
    usages, definitions, and blocks. The schema is:
        usage (n) -- (1) definition (n) -- (1) block_type
    """

    def create_usage(self, def_id):
        """Create a new usage id bound to the given definition id."""
        definition_key = ndb.Key(store.DefinitionEntity, str(def_id))
        assert definition_key.get() is not None
        usage_id = generate_id()
        usage = store.UsageEntity(id=usage_id)
        usage.definition_id = def_id
        usage.put()
        return usage_id

    def create_definition(self, block_type):
        """Create a new definition id, bound to the given block type.

        Args:
            block_type: str. The type of the XBlock for this definition.

        Returns:
            str. The id of the new definition.
        """
        definition_id = generate_id()
        definition = store.DefinitionEntity(id=definition_id)
        definition.block_type = block_type
        definition.put()
        return definition_id


class Runtime(xblock.runtime.Runtime):
    """An XBlock runtime which uses the App Engine datastore."""

    def __init__(
            self, id_reader=None, field_data=None, student_id=None, **kwargs):
        super(Runtime, self).__init__(
            id_reader or IdReader(),
            field_data or xblock.runtime.KvsFieldData(store.KeyValueStore()),
            **kwargs)
        self.user_id = student_id
