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
A WSGI app represeting the OCCI api.
'''

from occi import backend
from occi import wsgi
from occi import core_model

from adapters import paas

import ConfigParser

from api import backends
from api import registry
from api import occi_ext

MIXIN_BACKEND = backend.MixinBackend()
SCHEME = 'http://schemas.openshift.com/template/app#'

CONFIG = ConfigParser.ConfigParser()
CONFIG.read('etc/defaults.cfg')
URI = CONFIG.get('OpenShift', 'uri')
GLUE = paas.OpenShiftAdapter(URI)

# For local testing :-P
# from tests import dummies
# GLUE = dummies.DummyPaas()


def _register_templates(app, auth_head):
    '''
    Register resource and app templates.
    '''
    # resource templates
    tmp = GLUE.list_gears(auth_head)['data']['capabilities']['gear_sizes']
    for item in tmp:
        res_temp = occi_ext.ResTemplate(SCHEME, item,
                                        related=[occi_ext.RES_TEMPLATE])
        app.register_backend(res_temp, MIXIN_BACKEND)

    # app templates
    tmp = GLUE.list_features(auth_head)['data']
    for item in tmp:
        if item['type'] == 'standalone':
            cat = occi_ext.AppTemplate(SCHEME, item['name'], related=[
                occi_ext.APP_TEMPLATE])
            app.register_backend(cat, MIXIN_BACKEND)


def _register_services(app, auth_head):
    '''
    Register available services.
    '''
    tmp = GLUE.list_features(auth_head)['data']
    for item in tmp:
        if item['type'] == 'embedded' and 'embedded' in item['tags']:
            key = '/component/' + item['name']
            res = core_model.Resource(key, occi_ext.COMPONENT, [],
                                      title=item['description'])
            app.registry.add_resource(key, res, None)


def _register_keys(app, auth_head):
    '''
    Register SSH keys.
    '''
    tmp = GLUE.list_keys(auth_head)['data']
    for item in tmp:
        key = '/public_key/' + item['name']
        res = core_model.Resource(key, occi_ext.KEY_KIND, [])
        res.attributes['occi.key.name'] = item['name']
        res.attributes['occi.key.content'] = item['content']
        res.attributes['occi.core.id'] = item['name']
        app.registry.add_resource(key, res, None)


class OpenShiftWrapperApp(wsgi.Application):
    '''
    Simple WSGI app wrapper.
    '''

    def __call__(self, environ, response):
        '''
        Simplistic security check.
        '''
        if 'HTTP_AUTHORIZATION' not in environ:
            response('401 Unauthorized', [])
            return ['Please provide authentication headers.']
        sec_obj = {'Authorization': environ['HTTP_AUTHORIZATION'],
                   'Accept': '*/*'}

        _register_templates(self, sec_obj)
        _register_services(self, sec_obj)
        _register_keys(self, sec_obj)

        return self._call_occi(environ, response, auth_header=sec_obj)


def get_app():
    '''
    Returns a WSGI compatible app.
    '''
    app_backend = backends.AppBackend(GLUE)
    service_link_back = backends.ServiceLink(GLUE)
    ssh_backend = backends.SshKeyBackend(GLUE)

    app = OpenShiftWrapperApp(registry=registry.Registry(GLUE))
    app.register_backend(occi_ext.APP, app_backend)
    app.register_backend(occi_ext.APP_STOP, app_backend)
    app.register_backend(occi_ext.APP_START, app_backend)
    app.register_backend(occi_ext.COMPONENT, backend.KindBackend())
    app.register_backend(occi_ext.COMP_LINK, service_link_back)
    app.register_backend(occi_ext.KEY_KIND, ssh_backend)

    return app
