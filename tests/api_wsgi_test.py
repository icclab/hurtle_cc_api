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
Unittests for the api wsgi module.
'''

from api import wsgi
from tests import dummies

import unittest


class WsgiTest(unittest.TestCase):

    # test for success

    def test_get_app_for_success(self):
        wsgi.GLUE = dummies.DummyPaas()
        app = wsgi.get_app()
        req = {'SERVER_NAME': 'localhost',
               'SERVER_PORT': '8888',
               'PATH_INFO': '/',
               'REQUEST_METHOD': 'GET',
               'HTTP_AUTHORIZATION': 'Basic foobar'}
        app.__call__(req, _ResponseMock())

    def test_auth_for_failure(self):
        wsgi.GLUE = dummies.DummyPaas()
        app = wsgi.get_app()
        req = {'SERVER_NAME': 'localhost',
               'SERVER_PORT': '8888',
               'PATH_INFO': '/',
               'REQUEST_METHOD': 'GET'}
        self.assertEqual(app.__call__(req, _ResponseMock()),
                         ['Please provide authentication headers.'])


class _ResponseMock(object):

    def __call__(self, *args, **kwargs):
        pass