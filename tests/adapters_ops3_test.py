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

from adapters import ops3

import mox
import json
from requests.models import Response
import requests


import unittest

NAMESPACE = 'mcn'


class TestOpenShiftAdapter(unittest.TestCase):
    '''
    Unittest for OpenShift V3 Adapter.
    '''


    #TODO: fix the expected request data

    def setUp(self):
        self.URI="https://master.ops3.cloudcomplab.ch:8443"
        self.ops3 = ops3.OpenShift3Adapter(self.URI, namespace='mcn', domain='.apps.ops3.cloudcomplab.ch')

        self.template_gen = ops3.SOTemplateGen(so_name='foo_name', namespace='foo_namespace', is_name='foo_is', base_url='foo_url', env={})

        self.mox = mox.Mox()

    def _gen_json_func(self, content):
        def my_json():
            return content
        return my_json

    def _setup_http(self, requests_to_mock):

        conn = self.mox.CreateMock(ops3.OpenShift3Connector)
        for req in requests_to_mock:
            method = req["method"]
            url = req["url"]
            data = req.get("data", {})
            headers = req.get("headers", self._get_auth_heads(''))
            verify = req.get("verify", False)
            allow_redirects = req.get("allow_redirects", False)
            return_code = req["return_code"]
            return_obj = req.get("return_obj", {})
            return_headers = req.get("return_headers", {})

            response = self.mox.CreateMock(Response)
            response.status_code = return_code
            response.reason = 'An Error occurred... blah blah'
            response.content = json.dumps(return_obj)
            response.headers = return_headers
            response.json = self._gen_json_func(return_obj)

            conn.request(method=method, url=url, data=data, headers=headers, verify=verify,
                         allow_redirects=allow_redirects).AndReturn(response)
        return conn

    def _get_auth_heads(self, _):
        return {'Authorization': 'Bearer kATRJzppj1I-LkzHNyBvmJ5Ak90yYhTt9Y4fLuV1Wio'}

    def test_request(self):
        url = 'http://localhost'
        self.conn = ops3.OpenShift3Connector(url)
        self.mox.StubOutWithMock(requests, 'get')
        self.mox.StubOutWithMock(requests, 'delete')
        self.mox.StubOutWithMock(requests, 'post')
        requests.get(allow_redirects=False, data={}, headers={}, url='http://localhost', verify=True).AndReturn(True)
        requests.delete(allow_redirects=False, data={}, headers={}, url='http://localhost', verify=True).AndReturn(True)
        requests.post(allow_redirects=False, data={}, headers={}, url='http://localhost', verify=True).AndReturn(True)
        self.mox.ReplayAll()
        self.assertTrue(self.conn.request(method='GET', url=url, headers={}, data=None, verify=True, allow_redirects=False))
        self.assertTrue(self.conn.request(method='DELETE', url=url, headers={}, data=None, verify=True, allow_redirects=False))
        self.assertTrue(self.conn.request(method='POST', url=url, headers={}, data=None, verify=True, allow_redirects=False))
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        with self.assertRaises(AttributeError) as context:
            self.conn.request('FOOBAR', url, {}, True)
        self.assertTrue('unsupported method specified' in context.exception)

    # def test_create_app_for_success(self):
    #     # data
    #     self.template_gen.env={}
    #     reqs = [{"method": 'POST',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/services',
    #              "data": json.dumps(self.template_gen.get_file('so_svc')),
    #              "return_code": 201,
    #              },
    #             {"method": 'POST',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs',
    #              "data": json.dumps(self.template_gen.get_file('so_dc')),
    #              "return_code": 201,
    #              },
    #             {"method": 'POST',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/routes',
    #              "data": json.dumps(self.template_gen.get_file('so_route')),
    #              "return_code": 201,
    #              }
    #             ]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     self.ops3.create_app('foo_name', 'foo_image', self._get_auth_heads(''), env={})
    #
    #     # assert
    #     self.mox.VerifyAll()
    #
    # def test_create_app_for_failure(self):
    #
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.create_app('', 'foo_image', '')
    #
    #     self.assertTrue('Please provide a valid identifier.' in context.exception)
    #
    #     # data
    #     self.template_gen.env={}
    #     reqs = [{"method": 'POST',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/services',
    #              "data": json.dumps(self.template_gen.get_file('so_svc')),
    #              "return_code": 201,
    #              },
    #             {"method": 'POST',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs',
    #              "data": json.dumps(self.template_gen.get_file('so_dc')),
    #              "return_code": 201,
    #              },
    #             {"method": 'POST',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/routes',
    #              "data": json.dumps(self.template_gen.get_file('so_route')),
    #              "return_code": 401,
    #              }
    #             ]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.create_app('foo_name', 'foo_image', self._get_auth_heads(''), env={})
    #
    #     # assert
    #     self.mox.VerifyAll()
    #     self.assertTrue('Cannot create Route foo_name' in context.exception)
    #
    #     # new data
    #     reqs[1]["return_code"] = 401
    #     reqs.pop()
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.create_app('foo_name', 'foo_image', self._get_auth_heads(''), env={})
    #
    #     # assert
    #     self.mox.VerifyAll()
    #     self.assertTrue('Cannot create DC foo_name' in context.exception)
    #
    #     # new data
    #     reqs[0]["return_code"] = 401
    #     reqs.pop()
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.create_app('foo_name', 'foo_image', self._get_auth_heads(''), env={})
    #
    #     # assert
    #     self.mox.VerifyAll()
    #     self.assertTrue('Cannot create Service foo_name' in context.exception)
    #
    # def test_create_app_for_sanity(self):
    #     # data
    #     self.template_gen.env={}
    #     reqs = [{"method": 'POST',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/services',
    #              "data": json.dumps(self.template_gen.get_file('so_svc')),
    #              "return_code": 201,
    #              },
    #             {"method": 'POST',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs',
    #              "data": json.dumps(self.template_gen.get_file('so_dc')),
    #              "return_code": 201,
    #              },
    #             {"method": 'POST',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/routes',
    #              "data": json.dumps(self.template_gen.get_file('so_route')),
    #              "return_code": 201,
    #              }
    #             ]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     app = self.ops3.create_app('foo_name', 'foo_image', self._get_auth_heads(''), env={})
    #
    #     # assert
    #     self.mox.VerifyAll()
    #     self.assertEqual(app['data'], {'id': 'foo_name', 'scalable': 'False'})

    # def test_retrieve_app_for_success(self):
    #     # data
    #     uid = 'foo_name'
    #     reqs = [{"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {'items': [{'metadata': {'annotations': {'openshift.io/deployment.phase': 'Complete' }}}]}
    #              }]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     self.ops3.retrieve_app('foo_name', self._get_auth_heads(''))
    #
    #     # assert
    #     self.mox.VerifyAll()

    # def test_retrieve_app_for_failure(self):
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.retrieve_app('', '')
    #
    #     self.assertTrue('Please provide a valid identifier.' in context.exception)
    #
    #     # data
    #     uid = 'foo_name'
    #     reqs = [{"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid,
    #              "return_code": 401,
    #              "return_obj": {'items': [{'metadata': {'annotations': {'openshift.io/deployment.phase': 'Complete' }}}]}
    #              }]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.retrieve_app('foo_name', self._get_auth_heads(''))
    #
    #     # assert
    #     self.mox.VerifyAll()
    #     self.assertTrue('Error while retrieving app with identifier foo_name' in context.exception)

    # def test_retrieve_app_for_sanity(self):
    #     # data
    #     uid = 'foo_name'
    #     reqs = [{"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {'items': [{'metadata': {'annotations': {'openshift.io/deployment.phase': 'Complete'}}},
    #                                       {'metadata': {'annotations': {'openshift.io/deployment.phase': 'Complete'}}},
    #                                       {'metadata': {'annotations': {'openshift.io/deployment.phase': 'Complete'}}},
    #                                       {'metadata': {'annotations': {'openshift.io/deployment.phase': 'Complete'}}},
    #                                       {'metadata': {'annotations': {'openshift.io/deployment.phase': 'Nope'}}}]}
    #              }]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     app, _ = self.ops3.retrieve_app('foo_name', self._get_auth_heads(''))
    #
    #     # assert
    #     self.mox.VerifyAll()
    #     self.assertEqual('foo_name.mcn.apps.ops3.cloudcomplab.ch', app['data']['app_url'])
    #     self.assertEqual(False, app['data']['state'])
    #     self.assertEqual('foo_name', app['data']['name'])
    #
    #     # data
    #     reqs[0]["return_obj"]["items"].pop()
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     app, _ = self.ops3.retrieve_app('foo_name', self._get_auth_heads(''))
    #     self.mox.VerifyAll()
    #     self.assertEqual(True, app['data']['state'])

    # def test_delete_app_for_success(self):
    #     uid = 'foo_name'
    #     # data
    #     reqs = [{"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/services/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/routes/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {'items': [{'metadata': {'name': uid}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {"items": [{'metadata': {'name': uid}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/pods?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {"items": [{'metadata': {'name': uid}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/pods/' + uid,
    #              "return_code": 200,
    #              }
    #             ]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     self.ops3.delete_app('foo_name', self._get_auth_heads(''))
    #
    #     # assert
    #     self.mox.VerifyAll()
    #
    # def test_delete_app_for_failure(self):
    #     # FIXME(dudo,ernm): better error handling in ops3.py and tests
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.delete_app('', '')
    #     self.assertTrue('Please provide a valid identifier.' in context.exception)
    #
    #     uid = 'foo_name'
    #     # data
    #     reqs = [{"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/services/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/routes/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {'items': [{'metadata': {'name': uid}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {"items": [{'metadata': {'name': uid}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/pods?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {"items": [{'metadata': {'name': uid}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/pods/' + uid,
    #              "return_code": 200,
    #              }
    #             ]
    #
    #     expected_errors = ['Could not delete service with uid ' + uid,
    #                        'Could not delete route with uid ' + uid,
    #                        'Could not retrieve deploymentconfigs',
    #                        'Could not delete deploymentconfig with uid ' + uid,
    #                        'Could not retrieve replicationcontrollers',
    #                        'Could not delete replicationcontroller with uid ' + uid,
    #                        'Could not retrieve pods',
    #                        'Could not delete pod with uid ' + uid]
    #     while len(reqs) > 0:
    #
    #         # prepare this loop
    #         reqs[len(reqs) - 1]["return_code"] = 400
    #         expected_error = expected_errors.pop()
    #
    #         # setup
    #         c = self._setup_http(reqs)
    #         self.ops3.conn = c
    #         self.ops3.get_auth_heads = self._get_auth_heads
    #
    #         # start
    #         self.mox.ReplayAll()
    #
    #         # execute
    #         with self.assertRaises(AttributeError) as context:
    #             self.ops3.delete_app('foo_name', self._get_auth_heads(''))
    #
    #         # assert
    #         self.assertTrue(expected_error in context.exception, msg=expected_error)
    #         self.mox.VerifyAll()
    #
    #         # rotate test
    #         reqs.pop()
    #
    # def test_delete_app_for_sanity(self):
    #     # check that multiple returned elements get iterated over
    #     uid = 'foo_name'
    #     # data
    #     reqs = [{"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/services/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/routes/' + uid,
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {'items': [{'metadata': {'name': uid + '-1'}}, {'metadata': {'name': uid + '-2'}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs/' + uid + '-1',
    #              "return_code": 200,
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/oapi/v1/namespaces/' + NAMESPACE + '/deploymentconfigs/' + uid + '-2',
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {"items": [{'metadata': {'name': uid + '-1'}}, {'metadata': {'name': uid + '-2'}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers/' + uid + '-1',
    #              "return_code": 200,
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/replicationcontrollers/' + uid + '-2',
    #              "return_code": 200,
    #              },
    #             {"method": 'GET',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/pods?labelSelector=name=' + uid,
    #              "return_code": 200,
    #              "return_obj": {"items": [{'metadata': {'name': uid + '-1'}}, {'metadata': {'name': uid + '-2'}}]}
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/pods/' + uid + '-1',
    #              "return_code": 200,
    #              },
    #             {"method": 'DELETE',
    #              "url": self.URI + '/api/v1/namespaces/' + NAMESPACE + '/pods/' + uid + '-2',
    #              "return_code": 200,
    #              }
    #             ]
    #
    #     # setup
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.ops3.get_auth_heads = self._get_auth_heads
    #
    #     # start
    #     self.mox.ReplayAll()
    #
    #     # execute
    #     self.ops3.delete_app('foo_name', self._get_auth_heads(''))
    #
    #     # assert
    #     self.mox.VerifyAll()

    # def test_get_auth_heads_for_success(self):
    #     reqs = [{"method": 'GET',
    #              "url": self.URI + '/oauth/authorize?response_type=token&client_id=openshift-challenging-client',
    #              "headers": {'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='},
    #              "allow_redirects": False,
    #              "return_code": 302,
    #              "return_headers": {
    #                  "Location": "https://master.ops3.cloudcomplab.ch:8443/oauth/token/display#access_token=kATRJzppj1I-LkzHNyBvmJ5Ak90yYhTt9Y4fLuV1Wio&expires_in=86400&token_type=bearer"
    #              }}]
    #     c = self._setup_http(reqs)
    #     self.ops3.conn = c
    #     self.mox.ReplayAll()
    #     self.ops3.get_auth_heads({'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='})
    #     self.mox.VerifyAll()

    # def test_get_auth_heads_for_failure(self):
    #     # without auth header
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.get_auth_heads({})
    #     self.assertTrue('No auth header provided' in context.exception)
    #
    #     # invalid auth header
    #     reqs = [{"method": 'GET',
    #              "url": self.URI + '/oauth/authorize?response_type=token&client_id=openshift-challenging-client',
    #              "headers": {'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='},
    #              "allow_redirects": False,
    #              "return_code": 401
    #              }]
    #     c = self._setup_http(reqs)
    #     self.mox.ReplayAll()
    #     self.ops3.conn = c
    #     with self.assertRaises(AttributeError) as context:
    #         self.ops3.get_auth_heads({'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='})
    #     self.assertTrue('Login Error' in context.exception)

    # def test_get_auth_heads_for_sanity(self):
    #     wanted_token = {'Authorization': 'Bearer kATRJzppj1I-LkzHNyBvmJ5Ak90yYhTt9Y4fLuV1Wio'}
    #
    #     reqs = [{"method": 'GET',
    #              "url": self.URI + '/oauth/authorize?response_type=token&client_id=openshift-challenging-client',
    #              "headers": {'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='},
    #              "allow_redirects": False,
    #              "return_code": 302,
    #              "return_headers": {
    #                  "Location": "https://master.ops3.cloudcomplab.ch:8443/oauth/token/display#access_token=kATRJzppj1I-LkzHNyBvmJ5Ak90yYhTt9Y4fLuV1Wio&expires_in=86400&token_type=bearer"
    #              }}]
    #     c = self._setup_http(reqs)
    #
    #     self.ops3.conn = c
    #
    #     self.mox.ReplayAll()
    #     auth_token = self.ops3.get_auth_heads({'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='})
    #     self.mox.VerifyAll()
    #     self.assertEqual(auth_token, wanted_token)
