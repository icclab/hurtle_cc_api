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
Unittests for the api backends module.
'''

from api import backends
from api import occi_ext
from occi import core_model

import dummies

import unittest


class AppBackendTest(unittest.TestCase):

    def setUp(self):
        self.dummy = dummies.DummyOpenShift2Adapter()
        self.cut = backends.AppBackend(self.dummy)
        self.extras = {'auth_header': {'Authorization': 'Basic foobar'}}
        self.entity = core_model.Resource('', occi_ext.APP, [])

    # test for failure

    def test_create_for_failure(self):
        # missing attr
        self.assertRaises(AttributeError, self.cut.create, self.entity, None)
        # missing template
        self.entity.attributes = {'occi.app.name': 'foo'}
        self.assertRaises(AttributeError, self.cut.create, self.entity, None)

    def test_action_for_failure(self):
        self.entity.attributes = {'occi.core.id': '527ade897f9c48d371000001'}
        self.assertRaises(AttributeError, self.cut.action, self.entity,
                          occi_ext.APP_START, {}, None)

    # test for sanity

    def test_create_scalable_for_sanity(self):
        self.entity.attributes = {'occi.app.name': 'foo',
                                  'occi.app.scale': True,
                                  'occi.app.scales_from': 3,
                                  'occi.app.scales_to': 80}
        self.entity.mixins = [occi_ext.AppTemplate('foo', 'bar'),
                              occi_ext.ResTemplate('foo', 'bar')]
        self.cut.create(self.entity, self.extras)
        self.assertTrue('occi.core.id' in self.entity.attributes)
        self.assertTrue('occi.app.name' in self.entity.attributes)
        self.assertTrue(self.entity.attributes['occi.app.scale'])

    def test_create_for_sanity(self):
        self.entity.attributes = {'occi.app.name': 'foo'}
        self.entity.mixins = [occi_ext.AppTemplate('foo', 'bar'),
                              occi_ext.ResTemplate('foo', 'bar')]
        self.cut.create(self.entity, self.extras)
        self.assertTrue('occi.core.id' in self.entity.attributes)
        self.assertTrue('occi.app.name' in self.entity.attributes)

    def test_retrieve_for_sanity(self):
        self.entity.attributes = {'occi.core.id': '532ac4db6c33f378ca000010'}
        self.cut.retrieve(self.entity, self.extras)
        self.assertTrue('occi.app.url' in self.entity.attributes)
        self.assertTrue('occi.app.repo' in self.entity.attributes)
        self.assertTrue('occi.app.state' in self.entity.attributes)
        self.assertTrue('occi.app.scale' in self.entity.attributes)
        self.assertTrue('occi.app.scales_from' in self.entity.attributes)
        self.assertTrue('occi.app.scales_to' in self.entity.attributes)

    def test_delete_for_sanity(self):
        self.entity.attributes = {'occi.core.id': '532ac4db6c33f378ca000010'}
        self.cut.delete(self.entity, self.extras)

    def test_action_for_sanity(self):
        self.entity.attributes = {'occi.core.id': '532ac4db6c33f378ca000010'}
        # retrieve
        self.cut.retrieve(self.entity, self.extras)
        self.assertEqual(self.entity.attributes['occi.app.state'], 'active')
        self.assertListEqual(self.entity.actions, [occi_ext.APP_STOP])
        self.cut.action(self.entity, occi_ext.APP_STOP, {}, self.extras)
        # verified stop
        self.cut.retrieve(self.entity, self.extras)
        self.assertEqual(self.entity.attributes['occi.app.state'], 'inactive')
        self.assertListEqual(self.entity.actions, [occi_ext.APP_START])
        self.cut.action(self.entity, occi_ext.APP_START, {}, self.extras)
        # verified start
        self.cut.retrieve(self.entity, self.extras)
        self.assertEqual(self.entity.attributes['occi.app.state'], 'active')


class ServiceLinkBackendTest(unittest.TestCase):

    def setUp(self):
        self.dummy = dummies.DummyOpenShift2Adapter()
        self.cut = backends.ServiceLink(self.dummy)
        self.src = core_model.Resource('123', occi_ext.APP, [])
        self.trg = core_model.Resource('abc', occi_ext.COMPONENT, [])
        self.extras = {'auth_header': {'Authorization': 'Basic foobar'}}
        self.entity = core_model.Link('', occi_ext.APP, [], self.src, self.trg)

    def test_create_for_sanity(self):
        self.cut.create(self.entity, self.extras)

    def test_delete_for_sanity(self):
        self.cut.delete(self.entity, self.extras)


class SshKeyBackendTest(unittest.TestCase):

    def setUp(self):
        self.dummy = dummies.DummyOpenShift2Adapter()
        self.cut = backends.SshKeyBackend(self.dummy)
        self.extras = {'auth_header': {'Authorization': 'Basic foobar'}}
        self.entity = core_model.Resource('/public_key/123',
                                          occi_ext.KEY_KIND, [])

    def test_create_for_failure(self):
        self.entity.attributes = {}
        self.assertRaises(AttributeError, self.cut.create, self.entity,
                          self.extras)

    def test_create_for_sanity(self):
        self.entity.attributes = {'occi.key.content': 'foobar'}
        self.cut.create(self.entity, self.extras)
        self.entity.attributes['occi.key.name'] = 'mykey'
        self.cut.create(self.entity, self.extras)

    def test_delete_for_sanity(self):
        self.entity.attributes = {'occi.core.id': 'mykey'}
        self.cut.delete(self.entity, self.extras)
