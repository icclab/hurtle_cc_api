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
Unittests for the paas module.
'''

from adapters import ops2

import json
import httplib
import mox
import unittest


class TestOpenShiftAdapter(unittest.TestCase):
    '''
    Unittest for OpenShift Adapter.
    '''

    def _setup_http(self, requests):
        conn = self.mox.CreateMock(httplib.HTTPSConnection)
        for item in requests:
            conn.request(item[0], item[1], mox.IsA(object),
                         mox.IsA(object)).AndReturn(None)
            response = self.mox.CreateMock(httplib.HTTPResponse)
            response.status = item[2]
            response.reason = 'A error blah blah.'
            conn.getresponse().AndReturn(response)
            response.read().AndReturn(json.dumps(item[3]))
            conn.close()
        return conn

    def setUp(self):
        self.mox = mox.Mox()
        self.cut = ops2.OpenShift2Adapter('http://demo:changeme@localhost:8443')

    # Test for success.

    def test_create_app_for_success(self):
        c = self._setup_http([('POST',
                               '/broker/rest/domain/mcn/applications', 201,
                               {})])

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.create_app('foo', 'python-2.7', 'small', {})
        self.mox.VerifyAll()

    def test_retrieve_app_for_success(self):
        reqs = [('GET', '/broker/rest/application/123', 200, {}),
                ('GET', '/broker/rest/application/123/gear_groups', 200, {})]
        c = self._setup_http(reqs)

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.retrieve_app('123', {})
        self.mox.VerifyAll()

    def test_delete_app_for_success(self):
        c = self._setup_http([('DELETE', '/broker/rest/application/123',
                               200, {})])

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.delete_app('123', {})
        self.mox.VerifyAll()

    def test_list_apps_for_success(self):
        c = self._setup_http([('GET', '/broker/rest/applications', 200, {})])

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.list_apps({})
        self.mox.VerifyAll()

    def test_list_features_for_success(self):
        c = self._setup_http([('GET', '/broker/rest/cartridges', 200, {})])

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.list_features({})
        self.mox.VerifyAll()

    def test_list_gears_for_success(self):
        c = self._setup_http([('GET', '/broker/rest/user', 200, {})])

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.list_gears({})
        self.mox.VerifyAll()

    def test_start_app_for_success(self):
        c = self._setup_http([('POST', '/broker/rest/application/123/events',
                               200, {})])

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.start_app('123', {})
        self.mox.VerifyAll()

    def test_stop_app_for_success(self):
        c = self._setup_http([('POST', '/broker/rest/application/123/events',
                               200, {})])

        self.mox.ReplayAll()
        self.cut.conn = c
        self.cut.stop_app('123', {})
        self.mox.VerifyAll()

    # Test for failure.

    def test_create_app_for_failure(self):
        self.assertRaises(AttributeError, self.cut.create_app, None, None,
                          None, None)
        reqs1 = [('POST', '/broker/rest/domain/mcn/applications', 422,
                  {'data': {'id': '527ade9d7f9c48d37100000a'},
                   'messages': 'oops'})]
        c1 = self._setup_http(reqs1)
        self.mox.ReplayAll()
        self.cut.conn = c1
        self.assertRaises(AttributeError, self.cut.create_app, 'foo',
                          'python-2.7', 'small', {})

    def test_retrieve_app_for_failure(self):
        self.assertRaises(AttributeError, self.cut.retrieve_app, None, None)
        # first call goes wrong
        reqs1 = [('GET', '/broker/rest/application/123', 404,
                  {'messages': 'Not found!'})]
        c1 = self._setup_http(reqs1)
        self.mox.ReplayAll()
        self.cut.conn = c1
        self.assertRaises(AttributeError, self.cut.retrieve_app, '123', {})
        # second call goes wrong
        reqs = [('GET', '/broker/rest/application/123', 200, {}),
                ('GET', '/broker/rest/application/123/gear_groups', 404,
                 {'messages': ['Not found!']})]
        c = self._setup_http(reqs)
        self.mox.ReplayAll()
        self.cut.conn = c
        self.assertRaises(AttributeError, self.cut.retrieve_app, '123', {})

    def test_delete_app_for_failure(self):
        self.assertRaises(AttributeError, self.cut.delete_app, None, None)
        reqs1 = [('DELETE', '/broker/rest/application/123', 404,
                  {'messages': 'deletion failed!'})]
        c1 = self._setup_http(reqs1)
        self.mox.ReplayAll()
        self.cut.conn = c1
        self.assertRaises(AttributeError, self.cut.delete_app, '123', {})

    def test_action_for_failure(self):
        c = self._setup_http([('POST', '/broker/rest/application/123/events',
                               422, {'messages': ['N/A']})])
        self.mox.ReplayAll()
        self.cut.conn = c
        self.assertRaises(AttributeError, self.cut.start_app, '123', {})

    def test_add_service_for_failure(self):
        c = self._setup_http([('POST', '/broker/rest/' +
                               'application/123/cartridges', 404,
                               {'messages': 'Cartridge not found.'})])
        self.mox.ReplayAll()
        self.cut.conn = c
        self.assertRaises(AttributeError, self.cut.add_service, '123',
                          'mongo', {})

    def test_delete_service_for_failure(self):
        c = self._setup_http([('DELETE', '/broker/rest/' +
                               'application/123/cartridge/mongo', 404,
                               {'messages': 'Cartridge not found.'})])
        self.mox.ReplayAll()
        self.cut.conn = c
        self.assertRaises(AttributeError, self.cut.delete_service, '123',
                          'mongo', {})

    def test_key_mgmt_for_failure(self):
        c1 = self._setup_http([('POST', '/broker/rest/user/keys', 433,
                                {'messages': 'Invalid key.'})])
        c2 = self._setup_http([('DELETE', '/broker/rest/user/keys/mykey', 404,
                                {'messages': 'key not found.'})])
        self.mox.ReplayAll()
        self.cut.conn = c1
        self.assertRaises(AttributeError, self.cut.add_key, 'mykey', 'foo',
                          {})
        self.cut.conn = c2
        self.assertRaises(AttributeError, self.cut.delete_key, 'mykey', {})
        self.mox.VerifyAll()

    # Test for sanity.

    def test_create_app_for_sanity(self):
        reqs1 = [('POST', '/broker/rest/domain/mcn/applications', 201,
                  {'data': {'id': '527ade9d7f9c48d37100000a'}})]
        reqs2 = [('GET',  '/broker/rest/application/527ade9d7f9c48d37100000a',
                  200, {}),
                 ('GET', '/broker/rest/application/527ade9d7f9c48d37100000a'
                         '/gear_groups', 200, {})]
        c1 = self._setup_http(reqs1)
        c2 = self._setup_http(reqs2)

        self.mox.ReplayAll()
        self.cut.conn = c1
        tmp = self.cut.create_app('foo', 'python-2.7', 'small', {})
        self.cut.conn = c2
        self.cut.retrieve_app(tmp['data']['id'], {})
        self.mox.VerifyAll()

    def test_delete_app_for_sanity(self):
        c1 = self._setup_http([('POST',
                                '/broker/rest/domain/mcn/applications', 201,
                                {'data': {'id': '527ade9d7f9c48d37100000a'}})])
        c2 = self._setup_http([('DELETE', '/broker/rest/' +
                                'application/527ade9d7f9c48d37100000a', 200,
                                {})])

        self.mox.ReplayAll()
        self.cut.conn = c1
        tmp = self.cut.create_app('foo', 'python-2.7', 'small', {})
        self.cut.conn = c2
        self.cut.delete_app(tmp['data']['id'], {})
        self.mox.VerifyAll()

    def test_add_remove_service_for_sanity(self):
        c1 = self._setup_http([('POST',
                                '/broker/rest/domain/mcn/applications', 201,
                                {'data': {'id': '527ade9d7f9c48d37100000a'}})])
        c2 = self._setup_http([('POST', '/broker/rest/' +
                                'application/foo/cartridges', 201,
                                {})])
        c3 = self._setup_http([('DELETE', '/broker/rest/' +
                                'application/foo/cartridge/mongodb-2.2', 200,
                                {})])
        c4 = self._setup_http([('DELETE', '/broker/rest/' +
                                'application/527ade9d7f9c48d37100000a', 200,
                                {})])
        self.mox.ReplayAll()
        self.cut.conn = c1
        res1 = self.cut.create_app('foo', 'python-2.7', 'small', {})
        self.cut.conn = c2
        res2 = self.cut.add_service('foo', 'mongodb-2.2', {})
        self.cut.conn = c3
        res2 = self.cut.delete_service('foo', 'mongodb-2.2', {})
        self.cut.conn = c4
        self.cut.delete_app(res1['data']['id'], {})
        self.mox.VerifyAll()

    def test_key_mgmt_for_sanity(self):
        c1 = self._setup_http([('GET', '/broker/rest/user/keys', 200,
                                {'data': []})])
        c2 = self._setup_http([('POST', '/broker/rest/user/keys', 201, {})])
        c3 = self._setup_http([('DELETE', '/broker/rest/user/keys/mykey', 200,
                                {})])
        self.mox.ReplayAll()
        self.cut.conn = c1
        self.cut.list_keys({})
        self.cut.conn = c2
        self.cut.add_key('mykey', 'foobar', {})
        self.cut.conn = c3
        self.cut.delete_key('mykey', {})
        self.mox.VerifyAll()
