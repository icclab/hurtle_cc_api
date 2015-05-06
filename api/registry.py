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
Registry for pyssf.
'''
import uuid

import logging

from api import occi_ext

from occi import registry
from occi import core_model

LOG = logging.getLogger()


class Registry(registry.NonePersistentRegistry):
    '''
    Registry for the API.
    '''

    def __init__(self, paas_backend):
        super(Registry, self).__init__()
        self.glue = paas_backend

    def add_resource(self, key, resource, extras):
        # XXX: figure out if this is a bugfix or mandatory.
        self.resources[resource.identifier] = resource

    def get_resources(self, extras):
        tmp = self.glue.list_apps(extras['auth_header'])
        for item in tmp['data']:
            uid = item['id']
            if '/app/' + uid not in self.resources:
                # generic part
                entity = core_model.Resource('/app/' + uid, occi_ext.APP, [])
                entity.attributes['occi.core.id'] = uid
                res_temp = self.get_category('/' + item['gear_profile'] +
                                             '/', extras)
                #app_temp = self.get_category('/' + item['framework'] +
                #                             '/', extras)
                # links to services
                for component in item['embedded']:
                    try:
                        srv_link_key = '/componentlink/' + str(uuid.uuid4())
                        target = self.get_resource('/component/' + component,
                                                   None)
                        source = entity
                        link = core_model.Link(srv_link_key,
                                               occi_ext.COMP_LINK, [],
                                               source, target)
                        self.add_resource(srv_link_key, link, None)
                        entity.links.append(link)
                    except KeyError:
                        LOG.debug('Skipping link to the component {}.'
                                  .format(component))
                entity.mixins = [res_temp] #, app_temp]
                self.add_resource('', entity, extras)
        # XXX: make this nicer
        available_res = self.resources.keys()
        for res_key in available_res:
            ids = [item['id'] for item in tmp['data']]
            if res_key.split('/')[2] not in ids and \
                    res_key.find('component') == -1 and \
                    res_key.find('public_key') == -1:
                self.delete_resource(res_key, extras)
        return super(Registry, self).get_resources(extras)
