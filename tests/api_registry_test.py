#   Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

'''
Unittests for the api registry module.
'''

from api import registry
from api import occi_ext
from occi import core_model

from tests import dummies

import unittest


class RegistryTest(unittest.TestCase):

    def setUp(self):
        self.cut = registry.Registry(dummies.DummyOpenShift2Adapter())
        self.res = core_model.Resource('/component/mongodb-2.2',
                                       occi_ext.COMPONENT, [])
        self.extras = {'auth_header': {'Authorization': 'Basic foobar'}}
        self.cut.add_resource('/component/mongodb-2.2', self.res, None)

    # test for success.

    def test_add_resource_for_success(self):
        ent = core_model.Resource('foo', None, None)
        self.cut.add_resource('foo', ent, None)

    def test_get_resources_for_success(self):
        self.cut.get_resources(self.extras)
