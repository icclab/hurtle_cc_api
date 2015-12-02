#   Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
#   Copyright 2015 Zuercher Hochschule fuer Angewandte Wissenschaften
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

"""
A WSGI app representing the OCCI api.
"""

import ConfigParser
import os

from occi import backend
from occi import wsgi
from occi import core_model

from adapters import ops2
from adapters import ops3
from api import backends
from api import registry
from api import occi_ext

MIXIN_BACKEND = backend.MixinBackend()
SCHEME = 'http://schemas.openshift.com/template/app#'

CONFIG = ConfigParser.ConfigParser()
CONFIG.read('etc/defaults.cfg')
GLUE_NAME = os.environ.data['GLUE_NAME'] or CONFIG.get('General', 'platform')
# TODO make a call against a URL and figure out via API what adapter should be used
NS = os.environ.data['NAMESPACE'] or CONFIG.get('OpenShift3', 'namespace')
if GLUE_NAME == 'OpenShift2':
    URI = CONFIG.get('OpenShift2', 'uri')
    GLUE = ops2.OpenShift2Adapter(URI)
elif GLUE_NAME == 'OpenShift3':
    URI = os.environ.data['URI'] or CONFIG.get('OpenShift3', 'uri')
    DOMAIN = os.environ.data['DOMAIN'] or CONFIG.get('OpenShift3', 'domain')
    GLUE = ops3.OpenShift3Adapter(uri=URI, namespace=NS, domain=DOMAIN)
else:
    raise AttributeError('No valid General/platform configured in etc/defaults.cfg')

# For local testing :-P
# from tests import dummies
# GLUE = dummies.DummyOpenShift2Adapter()


def _register_templates(app, auth_head):
    """
    Register resource and app templates.
    """
    # resource templates
    # No sense in OpS3
    # TODO move check one-level up
    if GLUE.PLATFORM == 'OpenShift2':
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
    """
    Register available services.
    """
    # No sense in OpS3
    # TODO move check one-level up
    if GLUE.PLATFORM == 'OpenShift2':
        tmp = GLUE.list_features(auth_head)['data']
        for item in tmp:
            if item['type'] == 'embedded' and 'embedded' in item['tags']:
                key = '/component/' + item['name']
                res = core_model.Resource(key, occi_ext.COMPONENT, [],
                                          title=item['description'])
                app.registry.add_resource(key, res, None)


def _register_keys(app, auth_head):
    """
    Register SSH keys.
    """
    # No sense in OpS3
    # TODO move check one-level up
    if GLUE.PLATFORM == 'OpenShift2':
        tmp = GLUE.list_keys(auth_head)['data']
        for item in tmp:
            key = '/public_key/' + item['name']
            res = core_model.Resource(key, occi_ext.KEY_KIND, [])
            res.attributes['occi.key.name'] = item['name']
            res.attributes['occi.key.content'] = item['content']
            res.attributes['occi.core.id'] = item['name']
            app.registry.add_resource(key, res, None)


class OpenShiftWrapperApp(wsgi.Application):
    """
    Simple WSGI app wrapper.
    """

    def __call__(self, environ, response):
        """
        Simplistic security check.
        """
        if 'HTTP_AUTHORIZATION' not in environ:
            response('401 Unauthorized', [])
            return ['Please provide authentication headers.']
        sec_obj = {'Authorization': environ['HTTP_AUTHORIZATION'],
                   'Accept': '*/*'}
        # Templates and Keys have no meaning in OpS3

        _register_templates(self, sec_obj)
        _register_services(self, sec_obj)
        _register_keys(self, sec_obj)

        return self._call_occi(environ, response, auth_header=sec_obj)


def get_app():
    """
    Returns a WSGI compatible app.
    """
    app_backend = backends.AppBackend(GLUE)
    service_link_back = backends.ServiceLink(GLUE)

    app = OpenShiftWrapperApp(registry=registry.Registry(GLUE))
    app.register_backend(occi_ext.APP, app_backend)
    app.register_backend(occi_ext.APP_STOP, app_backend)
    app.register_backend(occi_ext.APP_START, app_backend)
    app.register_backend(occi_ext.COMPONENT, backend.KindBackend())
    app.register_backend(occi_ext.COMP_LINK, service_link_back)
    if GLUE_NAME == 'OpenShift2':
        ssh_backend = backends.SshKeyBackend(GLUE)
        app.register_backend(occi_ext.KEY_KIND, ssh_backend)

    return app
